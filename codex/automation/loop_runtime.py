from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from hooks.core.loop_engine import decide_loop_action
from hooks.redteam_state import RedTeamState

from .artifact_store import ArtifactStore
from .decision_tree import ReconContext, select_decision_path
from .executor import ExecutionResult, Executor
from .gate_engine import GateResult, evaluate_artifact_gate, evaluate_tool_gate, evaluate_scope_gate, evaluate_rhythm_gate, aggregate_gates
from .loop_recorder import LoopRecorder
from .loop_state import LoopRuntimeState
from .planner import AutomationPlan, create_automation_plan
from .quick_cards import build_quick_card, should_refresh_quick_card
from .rhythm import classify_rhythm
from .scope_gate import Scope, ScopeGate
from .tool_registry import ToolRegistry


@dataclass(frozen=True)
class LoopRuntimeResult:
    state: LoopRuntimeState
    decision: object
    plan: AutomationPlan
    execution_results: tuple[ExecutionResult, ...] = ()
    gate_results: tuple[object, ...] = ()
    artifacts: tuple[str, ...] = ()
    next_step: str = ""
    brief: str = ""
    quick_card: str = ""
    exited: bool = False


class LoopRuntime:
    def __init__(
        self,
        *,
        log_root: Path,
        executor: Executor | None = None,
        tool_config_paths: Sequence[str | Path] | None = None,
        artifact_root: Path | None = None,
        scope: Scope | None = None,
        max_retries: int = 0,
        recon_ctx: ReconContext | None = None,
    ) -> None:
        self.recorder = LoopRecorder(log_root)
        self._executor_provided = executor is not None
        self.executor = executor or Executor(plan_only=True)
        self.tool_config_paths = tool_config_paths
        self.artifact_store = ArtifactStore(artifact_root or (log_root / "artifacts"))
        self.scope = scope or Scope()
        self.max_retries = max(0, int(max_retries or 0))
        self.recon_ctx = recon_ctx

    def run_once(self, state: LoopRuntimeState) -> LoopRuntimeResult:
        """Execute a single Observe-Decide-Act-Verify-Record iteration."""
        if state.automation_mode == "active" and not self._executor_provided and self.executor.plan_only:
            self.executor = Executor(plan_only=False)
        path = select_decision_path(state.objective, phase=state.phase, recon_ctx=self.recon_ctx)
        plan = create_automation_plan(
            objective=state.objective,
            phase=state.phase,
            tool_config_paths=self.tool_config_paths,
            required_capabilities=path.required_capabilities,
        )
        tool_gate = evaluate_tool_gate(
            required_capabilities=path.required_capabilities,
            missing_capabilities=plan.missing_capabilities,
            plan_only_allowed=state.automation_mode != "active",
        )
        execution_results: list[ExecutionResult] = []
        scope_gate_results: list[GateResult] = []
        saved_artifacts: list[str] = []
        target = state.notes.get("target") if isinstance(state.notes, dict) else ""
        if tool_gate.passed:
            registry = ToolRegistry()
            for step in plan.steps:
                registry.register_selected(
                    capability=step.required_capability,
                    preferred_tool=step.preferred_tool,
                    selected_tool=step.tool,
                    risk=step.risk,
                    fallback_reason=step.fallback_reason,
                )
                scope_decision = ScopeGate(self.scope).check_tool(
                    step.tool,
                    {"target": target} if target else {},
                    registry,
                )
                scope_gate_results.append(
                    GateResult(
                        gate_name="Scope Gate",
                        grade="pass" if scope_decision.allowed else "blocked",
                        missing=(scope_decision.reason,) if not scope_decision.allowed else (),
                        reasons=(scope_decision.reason,),
                        next_required_action="execute" if scope_decision.allowed else "fix_scope_or_target",
                    )
                )
                if not scope_decision.allowed:
                    execution_results.append(
                        ExecutionResult(
                            step_id=step.id,
                            tool=step.tool,
                            capability=step.required_capability,
                            status="blocked",
                            artifact_type=step.expected_artifact,
                            error=scope_decision.reason,
                            retryable=False,
                            fallback_candidate="" if step.fallback_reason == "preferred_tool_available" else step.preferred_tool,
                            next_hint="fix_scope_or_target",
                        )
                    )
                    break
                result = self.executor.run_step(step, args={"target": target} if target else {})
                retry_count = 0
                while result.status == "failed" and result.retryable and retry_count < self.max_retries:
                    execution_results.append(result)
                    retry_count += 1
                    result = self.executor.run_step(step, args={"target": target} if target else {})
                if result.status == "success" and result.artifact_payload is not None:
                    artifact_path = self.artifact_store.save(result.artifact_type, result.artifact_payload)
                    result = ExecutionResult(
                        step_id=result.step_id,
                        tool=result.tool,
                        capability=result.capability,
                        status=result.status,
                        artifact_type=result.artifact_type,
                        artifact_path=str(artifact_path),
                        summary=result.summary,
                        error=result.error,
                        retryable=result.retryable,
                        fallback_candidate=result.fallback_candidate,
                        next_hint=result.next_hint,
                        artifact_payload=result.artifact_payload,
                    )
                    saved_artifacts.append(result.artifact_type)
                execution_results.append(result)
                if result.status in {"failed", "blocked"}:
                    break

        available_artifacts = tuple(dict.fromkeys((*state.recent_artifacts, *saved_artifacts)))
        artifact_gate = evaluate_artifact_gate(
            expected_artifacts=path.expected_artifacts,
            available_artifacts=available_artifacts,
            stagnation_count=state.stagnation_count,
            phase=state.phase,
        )
        rhythm = classify_rhythm(
            stagnation_count=state.stagnation_count,
            tool_failure_count=state.tool_failure_count
            + len([item for item in execution_results if item.status in {"failed", "blocked"}]),
            pseudo_complete_count=state.pseudo_complete_count,
            loop_iteration=state.loop_iteration,
        )

        redteam_state = RedTeamState(
            mode=state.mode,
            phase=state.phase,
            workflow_phase=state.workflow_stage,
            selected_path=path.path,
            evidence_level=state.evidence_level,
            stagnation_count=state.stagnation_count,
            pseudo_complete_count=state.pseudo_complete_count,
            current_task_id=state.current_task_id,
            session_id=state.session_id,
        )
        execution_required = bool(path.required_capabilities or plan.required_capabilities or plan.steps)
        execution_ok = bool(execution_results) and all(item.status == "success" for item in execution_results)
        verify_ok = execution_ok if execution_required else True
        if not execution_required:
            execution_gate = GateResult(
                gate_name="Execution Gate",
                grade="pass",
                reasons=("execution_not_required",),
                next_required_action="advance",
            )
        elif execution_ok:
            execution_gate = GateResult(
                gate_name="Execution Gate",
                grade="pass",
                reasons=("execution_succeeded",),
                next_required_action="advance",
            )
        elif not execution_results:
            execution_gate = GateResult(
                gate_name="Execution Gate",
                grade="soft_fail",
                reasons=("execution_not_attempted",),
                next_required_action="register_adapter_or_retry",
            )
        else:
            execution_gate = GateResult(
                gate_name="Execution Gate",
                grade="soft_fail",
                reasons=("execution_incomplete",),
                next_required_action="retry_or_fallback",
            )
        failed_results = [item for item in execution_results if item.status in {"failed", "blocked", "skipped"}]
        if failed_results:
            first = failed_results[0]
            missing = tuple(
                dict.fromkeys(
                    item.error or item.summary or item.status
                    for item in failed_results
                    if item.error or item.summary or item.status
                )
            )
            execution_gate = GateResult(
                gate_name="Execution Gate",
                grade="blocked" if first.status == "blocked" else "soft_fail",
                missing=missing,
                reasons=missing or (first.status,),
                next_required_action=first.next_hint or "fix_execution_path",
                hint=first.error or first.summary or first.status,
            )
        next_action = getattr(path, "next_action", "")
        rhythm_gate = evaluate_rhythm_gate(
            stagnation_count=state.stagnation_count,
            pivot_hints=(next_action,) if next_action else (),
        )
        control_gate = aggregate_gates(artifact_gate, tool_gate, *scope_gate_results, execution_gate, rhythm_gate)
        if control_gate.is_blocked:
            from hooks.core.loop_engine import LoopDecision
            decision = LoopDecision(
                action="blocked",
                reason="control_gate_blocked",
                next_stage=state.workflow_stage,
                next_step=control_gate.next_required_action or "resolve_blocking_gate",
                trigger="control_gate_blocked",
                feedback_gate=",".join(control_gate.reasons) or control_gate.hint or "Control Gate",
                exit_condition="resolve_blocking_gate",
                required_artifact=",".join(control_gate.missing),
            )
        elif control_gate.should_pivot:
            from hooks.core.loop_engine import LoopDecision
            decision = LoopDecision(
                action="pivot",
                reason="control_gate_pivot",
                next_stage=state.workflow_stage,
                next_step=control_gate.next_required_action or "use_pivot_hints",
                trigger="control_gate_pivot",
                feedback_gate=",".join(control_gate.reasons) or control_gate.hint or "Control Gate",
                exit_condition="select_new_path",
                required_artifact=",".join(control_gate.missing),
            )
        else:
            decision = decide_loop_action(
                state=redteam_state,
                evidence_level="partial" if control_gate.grade == "soft_fail" else state.evidence_level,
                gate_ok=control_gate.passed,
                verify_passed=control_gate.passed and verify_ok,
                taskbook={"todo_items": [{"id": state.current_task_id or "task-1"}]},
                current_task_id=state.current_task_id or "task-1",
            )
        self.recorder.record_decision(
            run_id=state.run_id,
            iteration=state.loop_iteration,
            decision=decision,
        )

        # FIX P3: merge notes instead of overwriting, increment loop_iteration
        merged_notes = {
            **(state.notes if isinstance(state.notes, dict) else {}),
            "decision_path_reason": path.reason,
            "rhythm_reason": rhythm.reason,
            "control_gate_grade": control_gate.grade,
            "control_gate_action": control_gate.next_required_action,
            "execution_gate_grade": execution_gate.grade,
            "execution_gate_action": execution_gate.next_required_action,
        }

        updated = LoopRuntimeState(
            run_id=state.run_id,
            session_id=state.session_id,
            objective=state.objective,
            mode=state.mode,
            automation_mode=state.automation_mode,
            phase=state.phase,
            router=state.router,
            leaf_skill=state.leaf_skill,
            workflow_stage=decision.next_stage,
            loop_iteration=state.loop_iteration + 1,  # FIX P3: was missing +1
            current_loop_type="observe-decide-act-verify-record",
            current_task_id=state.current_task_id,
            selected_path=path.path,
            required_capabilities=path.required_capabilities,
            selected_tools=tuple(step.tool for step in plan.steps),
            missing_capabilities=plan.missing_capabilities,
            recent_artifacts=available_artifacts,
            evidence_level="confirmed" if artifact_gate.passed else state.evidence_level,
            gate_results=(artifact_gate, tool_gate, *scope_gate_results, execution_gate, rhythm_gate),
            drift_score=rhythm.drift_score,
            rhythm_state=rhythm.state,
            stagnation_count=state.stagnation_count,
            tool_failure_count=state.tool_failure_count
            + len([item for item in execution_results if item.status in {"failed", "blocked"}]),
            pseudo_complete_count=state.pseudo_complete_count,
            last_action=decision.action,
            last_reason=decision.reason,
            next_step=decision.next_step,
            notes=merged_notes,  # FIX P3: merged notes preserving target
        )

        quick_card = ""
        if should_refresh_quick_card(decision, loop_iteration=state.loop_iteration):
            quick_card = build_quick_card(
                objective=state.objective,
                selected_path=path.path,
                decision=decision,
                recent_artifacts=available_artifacts,
            )
        brief_lines = [
            f"[loop:{decision.action}]",
            f"[loop-trigger:{decision.trigger}]",
            f"[feedback-gate:{decision.feedback_gate}]",
            f"[exit-condition:{decision.exit_condition}]",
            f"[path:{path.path}]",
            f"[artifacts:{','.join(available_artifacts) or 'none'}]",
        ]
        if execution_results:
            statuses = ",".join(sorted({item.status for item in execution_results}))
            brief_lines.append(f"[execution:{statuses}]")
        brief_lines.append(f"[rhythm-gate:{rhythm_gate.grade}]")
        brief_lines.append(f"[next-step:{decision.next_step}]")

        exited = decision.action in {"advance", "exit_skill", "report", "blocked"}

        return LoopRuntimeResult(
            state=updated,
            decision=decision,
            plan=plan,
            execution_results=tuple(execution_results),
            gate_results=updated.gate_results,
            artifacts=available_artifacts,
            next_step=decision.next_step,
            brief="\n".join(brief_lines),
            quick_card=quick_card,
            exited=exited,
        )

    def run_until_exit(
        self,
        state: LoopRuntimeState,
        *,
        max_iterations: int = 5,
    ) -> LoopRuntimeResult:
        """Run the loop repeatedly until an exit condition or max_iterations.

        Exit conditions:
        - decision.action in {"advance", "exit_skill", "report", "blocked"}
        - reached max_iterations
        - consecutive missing_capability (tool degradation dead-end)
        """
        current_state = state
        last_result: LoopRuntimeResult | None = None
        consecutive_missing = 0

        for _ in range(max(1, max_iterations)):
            result = self.run_once(current_state)
            last_result = result

            # Check exit
            if result.exited:
                return result

            # Check consecutive missing capability
            if result.state.missing_capabilities:
                consecutive_missing += 1
                if consecutive_missing >= 2:
                    return result
            else:
                consecutive_missing = 0

            # Advance state for next iteration
            current_state = result.state

        # max_iterations reached
        return last_result  # type: ignore[return-value]
