from __future__ import annotations

from dataclasses import replace
from typing import Optional

from redteam_state import RedTeamState, load_state, reset_state, save_state


def load_runtime_state() -> RedTeamState:
    return load_state()


def save_runtime_state(state: RedTeamState) -> None:
    save_state(state)


def reset_runtime_state() -> RedTeamState:
    return reset_state()


def update_mode(state: RedTeamState, mode: str, phase: Optional[str] = None) -> RedTeamState:
    state = replace(state, mode=mode, phase=phase or state.phase)
    save_runtime_state(state)
    return state
