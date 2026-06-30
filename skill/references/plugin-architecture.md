# Fact-Check Hermes Plugin Architecture

> Built June 2026. Plugin at `~/.hermes/plugins/fact-check/`. GitHub: `onezion12344/fact-check-agent`

## Overview

The fact-check framework runs at **two levels** simultaneously:

| Level | Mechanism | What it handles | Trigger |
|:------|:----------|:----------------|:--------|
| **Plugin** | Native Hermes Plugin (lifecycle hooks) | Phase 0.5 (pre-answer), post-check, verify_claims tool | Automatic — fires via hooks every turn |
| **Skill** | Skill loaded on demand | Full Round 1-4 (SIFT → CoVe+FIRE → FABLE → Truth Sandwich) | Manual — `/skill fact-check` or auto-triggered by agent |

The Plugin handles the **always-on** verification layer (every message gets a quick scan). The Skill handles the **deep audit** (multi-round, multi-agent, full web verification). They share the same methodology but serve different latency/cost profiles.

## Plugin File Structure

```
~/.hermes/plugins/fact-check/
├── plugin.yaml       Manifest (name, version, description)
├── __init__.py       register() — wires hooks, tools, commands
├── verify.py         Core engine — search, pattern detection, formatting
└── cache/            Diagnostic logs (verify-<timestamp>.json)
```

## Registered Hooks

### `pre_llm_call` — Phase 0.5 (Pre-answer Verification)

Fires **once per turn**, before the LLM tool-calling loop starts.

**Flow:**
1. Fast regex pre-check (`_has_question_marker`) — skips non-factual questions without LLM call
2. If patterns match → `ctx.llm.complete()` to classify: "does this question ask about prices/times/addresses/numbers?"
3. If yes → `ctx.llm.complete()` to extract specific claims as JSON array
4. Time-sensitive claims (prices, hours, addresses) → web search via `ddgs` (DuckDuckGo, free)
5. Non-time-sensitive claims → marked as ⚠️ (general knowledge)
6. Results formatted and injected via `return {"context": verified_info}`

**Key constraint:** Must return quickly (<3s) — blocks the agent's response. Heavy verification deferred to Round 2 (via verify_claims tool or delegate_task).

### `transform_llm_output` — Post-answer Lightweight Check

Fires after the tool-calling loop completes, **before** the response is delivered.

**Flow:**
1. Check length ≥300 chars and factual marker count ≥5
2. Run `verify.fast_post_check()` — regex-only, no LLM calls
3. If issues found (unattributed prices, missing citations), append Truth Sandwich block
4. Otherwise return None (no modification)

**Designed to be fast** — no web search, no LLM call. The full 4-round audit is what the Skill does.

## Registered Tool

### `verify_claims`

Agent-called tool for web-search verification of specific claims.

**Schema:**
```json
{
  "claims": ["string array of claims to verify"]
}
```

**Output:** Structured per-claim results with ✅🔧⚡❌ status, independent source count, and source URLs.

**Internal logic:**
- `verify.batch_verify()` → per-claim: `verify.verify_single()`
- `multi_angle_search()` — searches from two different query angles, deduplicates by URL
- Requires ≥2 independent domains for ✅ status (IFCN standard)
- Diagnostic log written to `cache/verify-<timestamp>.json`

## Search Engine

Uses `ddgs` package (DuckDuckGo search) — **free, no API key required.**

```python
from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text(query, max_results=3))
```

`pip install ddgs` if not present. The old `duckduckgo_search` package is deprecated (v8 → v9 renamed).

## Lifecycle Integration vs Skill

The Plugin and Skill are designed as **complementary**, not redundant.

| Scenario | Plugin does | Skill does |
|:---------|:------------|:-----------|
| User asks "XX多少钱" | Phase 0.5: search + inject context | — |
| Agent sends dense reply | Post-check: append visibility note | Round 1-4: full SIFT → FIRE → FABLE → Truth Sandwich |
| Agent needs to verify a specific claim | Agent calls `verify_claims` tool | Full multi-round via delegate_task |
| Emergency / time-sensitive | Phase 0.5 skipped (deferred) | — |

**"先计划不工程" rule:** When the user asks for a plan before building, do the research first, present options with tradeoffs, let them pick. Don't jump to implementation.

## Known Pitfalls

- **`pre_llm_call` fires every turn** — must return fast. Heavy verification goes in the tool or sub-agent.
- **`ctx.llm.complete()` borrows the user's active model** — can be expensive if called every turn. The regex pre-filter avoids this.
- **`transform_llm_output` cannot do async work** — the user blocks waiting for the response. Keep it regex-only (fast_post_check).
- **DuckDuckGo rate limits** — ~1 req/sec. Acceptable for single-claim verification, not for bulk.
- **Plugin loads on `/new`** — changes require session reset, not just a new turn.

## Future Directions

- Add `post_llm_call` hook for async full Round 1-4 (non-blocking, sends correction as follow-up)
- Add verification memory/cache (avoid re-verifying same claim within session)
- Add `verify_claims` auto-call: agent automatically calls the tool when response contains ≥5 price markers
