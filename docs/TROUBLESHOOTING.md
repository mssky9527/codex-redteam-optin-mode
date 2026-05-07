# Troubleshooting

## Chinese triggers do not work
- verify UTF-8 file encoding
- verify the hook decodes stdin via UTF-8/GB18030 fallback

## Hooks load but mode never changes
- validate `hooks.json`
- ensure `codex_hooks = true`

## Session feels polluted
- red-team mode should be explicit only
- start a new session to confirm reset
