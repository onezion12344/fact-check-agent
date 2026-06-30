# Double-Check Rename & Merge (v2.0.0)

This skill was renamed from `fact-check` → `double-check` on 2026-06-23 and merged with the former `logic-theory-check` skill.

## What Changed

| Before | After |
|:-------|:------|
| `fact-check` skill (v1.x) | `double-check` skill (v2.0.0) |
| `logic-theory-check` skill | Absorbed into double-check |
| Separate landing pages | Single page at factcheck.onezion.top |
| GH Pages deployment | CF Tunnel at onezion.top |

## Plugin Directory

The Hermes Plugin is at `~/.hermes/plugins/fact-check/` (directory not yet renamed). Config references it as `double-check`:

```yaml
# ~/.hermes/config.yaml
plugins:
  enabled:
  - double-check  # resolves to ~/.hermes/plugins/double-check/
```

If the plugin doesn't load after rename, check that the directory name matches:
```bash
mv ~/.hermes/plugins/fact-check ~/.hermes/plugins/double-check
```

## Old Names Still Work

- `skill_view("fact-check"...` still resolves (Hermes finds by name match in skill dir)
- GitHub repo remains `onezion12344/fact-check-agent` (can't rename without breaking URLs)
- GH Pages still at `onezion12344.github.io/fact-check-agent/`

## Loading This Skill

```bash
/skill double-check         # fact + logic + theory
skill_view("double-check")  # full SKILL.md
```
