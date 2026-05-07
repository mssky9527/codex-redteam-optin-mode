from __future__ import annotations

import io
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "codex" / "hooks" / "hook-security-context-hook.py"
SESSION = ROOT / "codex" / "hooks" / "session-start-context.py"


class FakeIn:
    def __init__(self, b: bytes) -> None:
        self.buffer = io.BytesIO(b)


def run_script(path: Path, payload: dict | None = None) -> str:
    old_stdin, old_stdout = sys.stdin, sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    data = b"" if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sys.stdin = FakeIn(data)
    try:
        runpy.run_path(str(path), run_name="__main__")
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout
    return buf.getvalue().strip()


class HookTests(unittest.TestCase):
    def test_enable_reverse_disable(self) -> None:
        run_script(SESSION)
        self.assertIn("enabled", run_script(HOOK, {"prompt": "进入红队模式"}))
        self.assertIn("phase:reverse", run_script(HOOK, {"prompt": "请从二进制反编译的角度分析这个程序"}))
        self.assertIn("phase:code-audit", run_script(HOOK, {"prompt": "请对这份源码做安全审计"}))
        self.assertIn("disabled", run_script(HOOK, {"prompt": "退出红队模式"}))


if __name__ == "__main__":
    unittest.main()
