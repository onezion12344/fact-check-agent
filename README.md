# Fact-Check Agent

> A hybrid fact-checking framework for AI agents. Pre-answer verification + post-answer deep audit. Merges journalism standards (SIFT, IFCN) with LLM academic research (CoVe, FIRE) into a 5-phase verification pipeline.

[![Version](https://img.shields.io/badge/version-1.1.0-6c5ce7?style=flat-square)](https://github.com/onezion12344/fact-check-agent)
[![Papers](https://img.shields.io/badge/academic_papers-12-00b894?style=flat-square)](https://github.com/onezion12344/fact-check-agent)
[![Standards](https://img.shields.io/badge/journalism_standards-10-74b9ff?style=flat-square)](https://github.com/onezion12344/fact-check-agent)
[![Multi-Agent](https://img.shields.io/badge/multi_agent_systems-9-e17055?style=flat-square)](https://github.com/onezion12344/fact-check-agent)

---

## 🚀 Quick Start

```
1. Load the skill:   skill_view(name='fact-check')
2. Ask a question with factual claims → Phase 0.5 auto-verifies first
3. Send a dense response → Round 1-4 auto-audits it
```

## 🌐 Live Demo

https://onezion12344.github.io/fact-check-agent/

## 📊 Pipeline Overview

| Phase | Name | When | What | Framework |
|:-----|:-----|:-----|:-----|:----------|
| 0 | Dedup Gate | Before any check | Emergency skip + content dedup | - |
| **0.5** | **Pre-answer** | **User asks fact question** | **Search ≥2 sources before answering** | **CoVe + FIRE** |
| 1 | SIFT Source Audit | After dense reply | Source attribution, mark ⚠️ guesses | SIFT, IMVAIN |
| 2 | CoVe+FIRE Verify | After SIFT | External cross-verification, ≥2 independent sources | CoVe (Meta 2023), FIRE (ACL 2025), IFCN |
| 3 | FABLE Impact | After verify | What actually matters? 🔴 Critical / 🟡 Experience / 🟢 Cosmetic | FABLE (HCI 2025) |
| 4 | Truth Sandwich | After impact | Structured correction delivery | Truth Sandwich, VeriFact-CoT |

## 🔬 Phase 0.5 — Pre-answer Verification (v1.1.0)

**New**: Before answering a question with factual claims, the agent automatically:

1. **Extracts** prices, times, addresses, names, and numbers from the user's question
2. **Prioritizes** — time-sensitive items (prices, hours, schedules, addresses) force external search immediately
3. **Searches** ≥2 independent sources in parallel
4. **Tags** output inline: ✅ confirmed / 🔧 corrected / ⚡ disputed / ❌ unverifiable
5. **Backstops** — if the full answer is ≥300 chars with ≥5 claims, runs Round 1-4 as supplement

### Skip Conditions

- Subjective questions ("which tastes better?")
- Conceptual explanations ("what is RAG?")
- File/URL analysis (goes through Round 1-4 SIFT)
- Emergency scenarios (defer all verification)

## 🔬 Rounds 1-4 — Post-answer Deep Audit

### Round 1: SIFT Source Audit
No external search. Every claim gets a tag:
- ✅ From source (quote-checked)
- ⚠️ Inferred/completed (needs external verification)
- ❌ Contradicts source

### Round 2: CoVe + FIRE Cross-Verification
- **CoVe**: Generate verification questions, answer them independently (don't re-read original text)
- **FIRE**: Iterative search — one search → insufficient → search again from different angle
- **IFCN**: ≥2 independent sources per claim
- Time-sensitive items (hours, prices, schedules, addresses) forced external — never trust internal knowledge

### Round 3: FABLE Impact Analysis
No new search. Grade each error:
- 🔴 **Critical Path**: Breaks user's plan (e.g., Correos closed Sunday → can't ship luggage)
- 🟡 **Experience**: Nice to fix but doesn't block (e.g., restaurant address off by one street)
- 🟢 **Cosmetic**: Text-only fixes (e.g., hotel name formatting)

### Round 4: Truth Sandwich Correction
Structured delivery:
1. What was written
2. What's wrong
3. What's correct + source
4. Action needed?

## 📚 Frameworks

### 📰 Journalism (5)
| Framework | Used In | Source |
|:----------|:--------|:-------|
| **SIFT** | Round 1 | Mike Caulfield, 2019 |
| **IFCN 5 Principles** | Round 2 | Poynter Institute |
| **IMVAIN** | Round 1 | Stony Brook Journalism |
| **PolitiFact 7-Step** | Reference | PolitiFact |
| **Truth Sandwich** | Round 4 | Journalist's field guide |

### 🧠 LLM Academic (4)
| Framework | Used In | Source |
|:----------|:--------|:-------|
| **CoVe** (Chain-of-Verification) | Round 2 | Meta, 2023 |
| **FIRE** (Iterative Retrieval) | Round 2 | ACL Findings 2025 |
| **VeriFact-CoT** | Round 4 | 2025 |
| **Fact-Audit** | Reference | 2025 |

### 🤖 Multi-Agent (3)
| Framework | Source |
|:----------|:-------|
| **VeriChain** | OpenReview 2026 |
| **TRUST Agents** | arXiv 2026 |
| **GKMAD** | Expert Systems 2026 |

## 🧪 Real-World Results

### Case 1: Camino de Santiago Planning
- Round 1: 23 ⚠️ (guessed) + 55 ✅ (from source)
- Round 2: 4 wrong addresses + 6 wrong prices/times found
- Round 3: 1 🔴 (Post office Sunday closure), 6 🟡, 3 🟢
- Key lesson: Hotel names all wrong (I guessed them), church names all right (from source). **⚠️ tags are the soul of SIFT.**

### Case 2: AI Foldable Phone Research
- Error rate trend: 9% → 3% → 0% over 6 verification rounds
- Prices consistently off by 2-2.6× (Nillkin keyboard: ¥200 → ¥500)
- BOW HB199 claimed touchpad — actually no touchpad
- GPU benchmarks mixed onscreen/offscreen — now forced to GSMArena only

## 💩 Production Pitfalls

| # | Trap | Rule |
|:-|:-----|:-----|
| 1 | 🐙 **Fabricated nutrition data** | Don't guess "15g protein" — actual is 29.8g (USDA) |
| 2 | ⚠️ **Dual-source contamination** | Tour brochure ≠ user's booking. Tag *intended* source |
| 3 | 💰 **1688 ≠ retail price** | Always check ≥3 platforms. Mark secondhand as "estimate" |
| 4 | 📊 **Mixed GPU benchmarks** | Only GSMArena + Notebookcheck UL Solutions |
| 5 | 🖊️ **OPPO Pen compatibility** | Goodix GP850 protocol — only Find N2/N3/N5/OnePlus Open |
| 6 | 🕐 **"Published yesterday"** | Time-sensitive items always need current verification |

## 🛠️ Parallel Execution

When Round 2 has ≥15 ⚠️ claims, parallelize across sub-agents:

```python
delegate_task(tasks=[
  {goal: "fact-check phone specs + root claims",  toolsets: ["web","terminal","skills"]},
  {goal: "fact-check accessories + prices",       toolsets: ["web","terminal","skills"]},
  {goal: "fact-check performance + features",     toolsets: ["web","terminal","skills"]}
])
```

Each sub-agent gets the full fact-check skill loaded and follows Round 2 methodology independently.

## 🤖 Compatibility

Built for [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research. The framework logic is methodology-agnostic — adaptable to any LLM-powered agent (Claude Code, AutoGPT, LangGraph, etc.).

## 📄 License

MIT — use freely, adapt, improve. Attribution appreciated.
