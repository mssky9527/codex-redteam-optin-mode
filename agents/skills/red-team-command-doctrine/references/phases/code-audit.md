# Code Audit

## Objective
Trace untrusted input to security-relevant sinks and identify one provable bug path.

## Enter when
Source code or decompiled logic is available and likely explains runtime behavior.

## Prioritize evidence
- entrypoints and routing
- auth/session/permission checks
- user-controlled input propagation
- dangerous sinks and side effects

## Low-noise path first
Prove one reachable path before cataloging every theoretical issue.

## Typical skills/tools
- `hack` plus the most specific vuln skill
- focused grep/search, targeted file reads, local tests

## Exit when
You can show a controllable path to a sink or falsify the hypothesis with a better next path.
