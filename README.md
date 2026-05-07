# Codex Red Team Opt-In Mode

> **Normal by default. Offensive only when explicitly armed.**

A lightweight, phase-aware Codex profile for offensive work.  
It keeps the assistant in **normal mode** by default and only activates **red-team routing** when the user explicitly turns it on.

## Highlights

- **Opt-in only** red-team mode
- **Structured JSON state**
- **Modular hooks**
- **Cross-platform installer**
- **Validation + tests**
- **Per-phase playbooks**
- **Low-noise / OPSEC-aware guidance**

## Quick Start

### Enable red-team mode

```text
进入红队模式
开启红队模式
/redteam on
enable red team mode
```

### Disable red-team mode

```text
退出红队模式
关闭红队模式
/redteam off
disable red team mode
```

### Install

```bash
python scripts/install.py
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

## Repository Layout

```text
codex/
  AGENTS.md
  hooks/
    session-start-context.py
    hook-security-context-hook.py
    redteam_state.py
    core/
agents/
  skills/
    red-team-command-doctrine/
      SKILL.md
      references/
docs/
scripts/
tests/
.github/
```

## Week 1 Scope

| Area | Status |
|---|---|
| Structured state | done |
| Modular hooks | done |
| Cross-platform installer | done |
| Validation | done |
| Basic tests | done |
| Docs baseline | done |

## Roadmap

| Week | Focus |
|---|---|
| Week 1 | hook architecture, installer, docs, validation |
| Week 2 | richer phase routing, better conflict checks |
| Week 3 | stronger OPSEC gates, mode profiles |
| Week 4 | release hardening, community feedback |

## Known Limitations

- This is a **control/profile layer**, not a full attack platform.
- Real execution depth still depends on your MCP/tooling surface.
- Hook behavior is intentionally lightweight to avoid context pollution.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
