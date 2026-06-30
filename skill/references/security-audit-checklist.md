# GitHub Public Submission Security Audit Checklist

> When submitting a project to a public competition (NOVA, hackathon, conference), audit all repos for sensitive information before making them public. One missed email draft or personal transcript can expose more than you intend.

## Audit Procedure

### 1. Clone fresh copies
```bash
git clone <repo-url> /tmp/audit-<name>
```

### 2. Search for sensitive patterns

```bash
# Personal identifiers
grep -rI "passport\|身份证\|passport.*[0-9]" /tmp/audit --include="*.md" --include="*.txt"
grep -rI "phone\|电话\|mobile" /tmp/audit --include="*.md" --include="*.txt"

# Email addresses (non-public)
grep -rI "[a-zA-Z0-9._%+-]\+@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}" /tmp/audit --include="*.md"

# File paths with usernames
grep -rI "/Users/\|/home/\|C:\\Users\\" /tmp/audit --include="*.md" --include="*.txt"

# API keys and tokens
grep -rI "api[_-]\?key\|apikey\|token\|secret" /tmp/audit --include="*.md" --include="*.yaml" --include="*.json"

# Cloudflare tunnel IDs, UUIDs
grep -rI "[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}" /tmp/audit --include="*.md" --include="*.yaml"
```

### 3. Hand-review these file types

| File Type | Risk | Action |
|:----------|:-----|:-------|
| `email-*.md` | 🔴 Full name, institution, activities | Delete |
| `audio_*.txt/vtt/srt` | 🔴 Personal conversation transcripts | Delete |
| `docs/*.md` | 🟡 May contain personal records | Review each |
| `*.json` | 🟡 Credentials, config tokens | Review each |
| Skill references with file paths | 🟡 Local paths | Replace `/Users/x` with `$HOME` or relative |

### 4. What's OK to keep

- GitHub username in repo URLs (public identity)
- Public domain names (factcheck.example.com)
- Competition materials (slides, abstract, benchmark) — these ARE the submission
- MIT license, README

### 5. Clean and push

```bash
# Remove sensitive files
git rm docs/email-draft.md docs/email-final.md
git rm audio_*.txt audio_*.vtt audio_*.srt audio_*.json audio_*.tsv

# Sanitize paths in remaining files
# Replace /Users/username with $HOME or relative references

git commit -m "Security audit: remove personal documents and sanitize paths"
git push
```

## Real Incidents (2026-06)

- **NOVA submission audit**: Found email drafts with full learning activity records, 150-line personal conversation transcript (Chinese), and `/Users/onezion12344` paths in 5 skill reference locations. All cleaned before public submission.

## Integration with Double-Check

This audit is a pre-submission step for any project backed by the Double-Check pipeline. If the very tool that verifies facts has its own repo leaking personal data, that's a credibility problem.

Run this audit before:
- NOVA / competition submissions
- Conference paper code releases
- Portfolio/public landing page pushes
- Any repo switch from private to public
