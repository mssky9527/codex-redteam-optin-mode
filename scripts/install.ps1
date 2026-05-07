param(
  [string]$CodexHome = "$env:USERPROFILE\.codex",
  [string]$AgentsHome = "$env:USERPROFILE\.agents",
  [switch]$DryRun,
  [switch]$Uninstall
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ArgsList = @("$RepoRoot\install.py", "--codex-home", $CodexHome, "--agents-home", $AgentsHome)
if ($DryRun) { $ArgsList += "--dry-run" }
if ($Uninstall) { $ArgsList += "--uninstall" }
python @ArgsList
