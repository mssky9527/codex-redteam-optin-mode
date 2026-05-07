# Mode State Machine

## States
- `normal`
- `redteam-light`
- `redteam-full`

## Entry
New top-level session always resets to `normal`.

## Transitions
- `normal` -> `redteam-light` on `进入红队模式`, `开启红队模式`, `/redteam on`, `enable red team mode`
- `normal` -> `redteam-full` on `/redteam full`
- `redteam-*` -> `normal` on `退出红队模式`, `关闭红队模式`, `/redteam off`, `disable red team mode`

## Invariants
- red-team mode is never the default
- session start never injects a heavy doctrine block
- explicit off immediately stops offensive injection
