# Reverse Engineering

## Objective
Recover control flow, trust boundaries, sensitive logic, and exploit-relevant conditions.

## Enter when
The critical path depends on understanding compiled behavior or hidden functionality.

## Prioritize evidence
- entrypoints and dispatch logic
- secrets, config, endpoints
- dangerous sinks and primitives
- anti-debug/packing layers

## Low-noise path first
Prefer static structure recovery and targeted debugging over broad dynamic thrashing.

## Typical skills/tools
- reverse / pwn / deobfuscation skills
- disassembler, debugger, strings, sandbox

## Exit when
You can explain the exploit-relevant path or route into loader analysis / payload with evidence.
