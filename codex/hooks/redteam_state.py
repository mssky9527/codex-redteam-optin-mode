from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


VALID_MODES = {"normal", "redteam-light", "redteam-full"}
VALID_OPSEC = {"strict", "balanced"}


@dataclass
class RedTeamState:
    mode: str = "normal"
    phase: str = "general"
    opsec_level: str = "balanced"
    last_changed: str = ""
    session_id: str = ""

    def normalized(self) -> "RedTeamState":
        mode = self.mode if self.mode in VALID_MODES else "normal"
        opsec = self.opsec_level if self.opsec_level in VALID_OPSEC else "balanced"
        phase = self.phase or "general"
        last_changed = self.last_changed or now_iso()
        session_id = self.session_id or str(uuid4())
        return RedTeamState(mode=mode, phase=phase, opsec_level=opsec, last_changed=last_changed, session_id=session_id)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_state() -> RedTeamState:
    return RedTeamState(mode="normal", phase="general", opsec_level="balanced", last_changed=now_iso(), session_id=str(uuid4()))


def state_path() -> Path:
    temp_dir = Path(os.environ.get("TEMP") or os.environ.get("TMP") or str(Path.home()))
    return temp_dir / "codex_redteam_mode_state.json"


def load_state() -> RedTeamState:
    path = state_path()
    if not path.exists():
        return default_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return RedTeamState(**raw).normalized()
    except Exception:
        return default_state()


def save_state(state: RedTeamState) -> None:
    state = state.normalized()
    state.last_changed = now_iso()
    state_path().write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")


def reset_state() -> RedTeamState:
    state = default_state()
    save_state(state)
    return state
