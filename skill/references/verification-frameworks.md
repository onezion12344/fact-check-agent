# Verification Frameworks — Academic & Professional Sources

> Aggregated from 12 academic papers + 10 journalism standards + 9 AI verification systems (June 2026).

## Journalism (oldest, most mature)

| Framework | Core Mechanism | Source |
|:--|------|------|
| **SIFT** | Stop → Investigate Source → Find Better Coverage → Trace claims | Mike Caulfield, 2019 |
| **IFCN 5 Principles** | 31 criteria, 170+ certified orgs | Poynter Institute |
| **IMVAIN** | Independent / Multiple / Verifies / Authoritative / Named sources | Stony Brook School of Journalism |
| **PolitiFact 7-Step** | Reporter + 3 editors, 6-level Truth-O-Meter rating | PolitiFact |
| **Truth Sandwich** | What was claimed → What's wrong → What's correct → Source → Action? | Journalist's field guide |

## LLM Academic (most relevant)

| Framework | Steps | Source |
|:--|------|------|
| **CoVe** (Chain-of-Verification) | Draft → Plan verification questions → Answer independently → Revise | Meta, 2023 |
| **FIRE** | Decompose atomic claims → Iterative retrieval → Verify → Refine | ACL Findings 2025 |
| **VeriFact-CoT** | CoT → Extract claims → Simulate evidence retrieval → Correct + cite | 2025, hallucination 25%→12% |
| **Fact-Audit** | Prototype simulation → Verify + reason → Adaptive update (multi-agent) | 2025, tested on 13 LLMs |

## Multi-Agent Verification

| Framework | Mechanism | Source |
|:--|------|------|
| **VeriChain** | Decompose + Verifier Agent + dynamic loop | OpenReview 2026 |
| **TRUST Agents** | Extract → Retrieve → Verify → Explain (4-agent pipeline) | arXiv 2026 |
| **GKMAD** | Guided debate → External knowledge → Judgment | Expert Systems 2026 |

## Key Insights Applied to This Skill

1. **SIFT from journalism works best for Round 1** — source attribution before verification, not after.
2. **CoVe's "independent answering" is critical for Round 2** — don't re-read your own text before verifying; search fresh.
3. **FIRE's iterative pattern**: one search → insufficient → search again from different angle → converge. Don't stop at first result.
4. **FABLE from HCI research**: Functional / Actionable / Blocking / Likelihood / Effort — this is the RIGHT taxonomy for impact analysis (Round 3), not a severity scale.
5. **IFCN's "≥2 independent sources" standard**: any ⚠️ claim must be confirmed by at least 2 unrelated sources.
6. **Time-sensitive forced external verification**: hours, prices, schedules, addresses change independently of source guides. Even "published yesterday" might be wrong — always verify current.
7. **Multi-agent anti-pattern**: domain-split agents (housing/route/food) all do the same Round 1-4 workflow → overlapping output → waste. Correct pattern: structural rounds (source audit / external verification / impact analysis), not domain splits.
