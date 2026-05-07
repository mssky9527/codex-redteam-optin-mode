param(
  [string]$CodexHome = "$env:USERPROFILE\.codex"
)
python "$PSScriptRoot\validate.py" --codex-home "$CodexHome"
