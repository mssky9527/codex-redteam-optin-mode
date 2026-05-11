# Codex Red Team Opt-In Mode

English | [中文](./README_ZH.md)

> **Normal by default. Offensive only when explicitly armed.**

A lightweight, phase-aware red-team profile for Codex.

This project keeps Codex in **normal mode** by default and only enables **offensive routing** when you explicitly turn it on. It adds:

- opt-in red-team mode
- lightweight hooks
- structured JSON mode state
- rule-first + semantic phase detection
- session-isolated mode state
- structured offensive task orchestration
- review gates for larger multi-step workflows

---

## Why this project

Most “always-on red-team prompts” fail in one of two ways:

1. they **pollute normal work**
2. they **blow up context** with heavy doctrine injection

This project takes the opposite approach:

- **normal mode stays normal**
- **red-team mode is explicit**
- **hooks stay small**
- **phase routing stays lightweight**

---

## Features

- **Opt-in only**
  - normal mode is the default
  - red-team mode only activates after explicit enable

- **Phase-aware routing**
  - web
  - ad
  - postex
  - reverse
  - code-audit
  - payload

- **Rule-first + semantic fallback**
  - direct matches win first
  - lightweight semantic fallback catches natural-language prompts that do not match exact keywords

- **Session isolation**
  - one session does not overwrite another session's mode state

- **Structured orchestration layer**
  - recon → strategy → exploit-dev → review → reporting
  - artifact schemas and gates
  - review-before-delivery workflow

- **Cross-platform install**
  - Windows / macOS / Linux

- **Validation and tests**
  - install validation
  - hook validation
  - orchestration gate validation
  - ordinary-mode cleanliness checks

---

## Install

### Python

```bash
python scripts/install.py
```

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

### macOS / Linux

```bash
python3 scripts/install.py
```

---

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

### Validate install

```bash
python scripts/validate.py
```

---

## How it works

### 1. Mode-gated behavior

The project starts in **normal** mode.

It does **not** inject offensive doctrine into ordinary work unless red-team mode is explicitly enabled.

### 2. Lightweight hooks

The runtime hooks are intentionally small:

- small session-start context
- no giant prompt injection
- no always-on offensive bias

### 3. Phase detection

Phase detection is **not regex-only**.

The runtime first tries:

1. explicit rules
2. lightweight semantic fallback

Examples:

- `程序启动后会释放文件并拉起子进程，帮我梳理执行链` → `reverse`
- `帮我从入口一路追到危险函数，看看权限边界哪里失守` → `code-audit`
- `拿到 shell 之后下一步应该先做什么` → `postex`

### 4. Structured orchestration

For larger tasks, the project includes a lightweight orchestration layer:

```text
recon -> strategy -> exploit-dev -> review -> reporting
```

This layer is **not** always-on runtime automation.  
It is a structured planning and gating framework.

---

## Repository Layout

```text
.github/
agents/
  skills/
    red-team-command-doctrine/
codex/
  AGENTS.md
  hooks/
  orchestrator/
docs/
scripts/
templates/
tests/
```

---

## Validation

The project validates:

- mode enable / disable
- phase routing
- semantic fallback
- ordinary-mode cleanliness
- session isolation
- orchestration gates

---

## Known Limitations

- this is a **control/profile layer**, not a full attack platform
- it does not include RAG or private knowledge retrieval
- `redteam-light` and `redteam-full` currently share the same routing behavior
- execution depth still depends on your MCP/tooling surface

---

## ⚠️ 免责声明 / Disclaimer

**本项目仅供授权渗透测试（Authorized Penetration Testing）和安全研究使用。**

### 重要声明
- 本工具 **仅限** 在您拥有 **明确书面授权** 的目标系统或环境中使用。
- 未经授权擅自用于任何生产系统、他人资产或非授权目标，属于违法行为，作者及贡献者不承担任何责任。
- 使用本项目即表示您同意自行承担所有风险，包括但不限于法律责任、数据泄露、系统损坏等后果。
- 作者及本项目不提供任何明示或暗示的担保，包括但不限于适销性、特定用途适用性及不侵权。

### Legal & Ethical Use Only
This project is intended **solely for educational purposes, authorized red team operations, and legal penetration testing** where you have explicit permission from the system owner.

- Any unauthorized use, including but not limited to attacking systems without consent, is strictly prohibited.
- The authors and contributors assume **no liability** for any damages, legal consequences, or losses resulting from the use or misuse of this tool.
- Users are fully responsible for ensuring their activities comply with all applicable local, national, and international laws.

**继续使用本项目 = 您已阅读、理解并同意以上全部条款。**

---

**如果您无法确保合法授权，请立即停止使用本项目。**
不需要回复，我存一下免责声明

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

MIT with an authorized-use-only notice.  
See [LICENSE](./LICENSE).
