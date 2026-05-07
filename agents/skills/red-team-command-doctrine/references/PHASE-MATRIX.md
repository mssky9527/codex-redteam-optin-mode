# Phase Matrix

| Phase | Objective | Primary skills | Typical MCP / tools | MITRE ATT&CK |
|---|---|---|---|---|
| recon | map attack surface and isolate one promising path | `recon-for-sec`, `recon-and-methodology` | web-access, Burp, targeted CLI recon | TA0043 |
| initial-access | land first controlled execution or auth | `initial-access-delivery`, exploit-specific skill | Burp, browser, delivery infrastructure | TA0001 |
| web-exploitation | prove one exploit chain | `hack` + specific web vuln skill | Burp, ffuf, repeater | TA0001 / TA0008 |
| credential-access | obtain or reuse credentials/tokens/keys | `credential-access-operations` | impacket, netexec, Burp | TA0006 |
| privilege-escalation | move from current user to stronger context | OS-specific privesc skill | Windows/Linux host ops | TA0004 |
| post-exploitation | triage host and choose the next hop | `post-exploitation-playbook` | shell, host-native enumeration | TA0007 |
| persistence-c2 | retain access with acceptable noise | `persistence-and-c2`, `red-team-opsec` | host ops, payload infra | TA0003 / TA0011 |
| lateral-movement | pivot to adjacent systems | lateral movement skills | SMB, WinRM, SSH, tunnels | TA0008 |
| ad-operations | abuse trust, identity, and control edges | `active-directory-*`, `ntlm-relay-coercion` | BloodHound, certipy, impacket | TA0006 / TA0008 |
| reverse-engineering | extract logic, sinks, secrets, and exploit conditions | reverse/pwn-oriented skills | disassemblers, debuggers, sandbox | TA0005 |
| code-audit | reason over source to find controllable bug paths | `hack` + specific review skill | grep, static review, local tests | TA0001 |
| cloud-iam-abuse | abuse cloud identity/control-plane permissions | `cloud-iam-abuse` | AWS/Azure/GCP CLI | TA0003 / TA0004 |
| reverse-loader-analysis | understand loader or sample behavior | `malware-loader-analysis` | sandbox, x64dbg, strings | TA0005 / TA0011 |
| payload-weaponization | choose a delivery-fit payload shape | `weaponization-and-payloads` | payload builders, launchers | TA0001 / TA0011 |
| reporting | preserve proof, impact, and next action | doctrine + report structure | docs | - |
