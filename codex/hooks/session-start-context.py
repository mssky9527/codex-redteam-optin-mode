#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from core import emit_hook_json, reset_runtime_state


def main() -> None:
    reset_runtime_state()
    context = "[mode] Default session mode is normal. Red-team mode is disabled unless the user explicitly enables it with phrases like 进入红队模式 or /redteam on."
    print(emit_hook_json("SessionStart", context))


if __name__ == "__main__":
    main()
