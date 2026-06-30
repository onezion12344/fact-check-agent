# Double-Check — AI Fact Verification Pipeline

[![Version](https://img.shields.io/badge/version-2.1.0-6c5ce7)]()
[![Frameworks](https://img.shields.io/badge/frameworks-31-00c853)]()
[![Catch Rate](https://img.shields.io/badge/catch_rate-100%25-448aff)]()
[![MIT](https://img.shields.io/badge/license-MIT-86868b)]()

A 5-phase verification pipeline that catches what LLMs miss. Merges 12 academic papers + 10 journalism standards into a production-grade agent plugin. Embeds directly into Hermes Agent as a native skill + plugin.

**🔴 Live: [factcheck.onezion.top](https://factcheck.onezion.top)**

---

## Why "Double-Check"?

There are two approaches to AI verification:

**Route A — Model Internalization** (OpenAI o3/o4, Claude, DeepSeek):
Train the model to know when to verify. Expensive, model-dependent, and the model can still misjudge.

**Route B — Double-Check** (External Enforcement):
Don't ask the model to verify. Enforce it from outside via plugin hooks.
Works with ANY model, TODAY.

The name "Double-Check" reflects the core insight: 
AI agents have bounded rationality — they won't verify enough on their own. 
Rather than waiting for better models, we build a system that double-checks 
every claim, regardless of which model generates it.

---

## Why

LLMs hallucinate. Even at 5% error rate, AI agents produce millions of incorrect facts daily. Existing solutions fall into two camps:

| | Journalism Standards | LLM Verification |
|:-|:--------------------|:-----------------|
| **Rigor** | ✅ IFCN 5 Principles, multi-source | ❌ Single-pass classification |
| **Speed** | ❌ Human-speed | ✅ LLM-speed |
| **Our approach** | Keep the rigor | Add the speed |

---

## Benchmark Results

40 questions × 3 judges (DeepSeek V4 Flash / V4 Pro / verified sources).

| Metric | Raw V4 Flash | + Double-Check |
|:-------|:------------:|:--------------:|
| Overall | 62.5% | **97.5%** |
| Prices | 50% → | 100% |
| Specs | 80% → | 100% |
| Stats | 50% → | 100% |
| Schedules | 70% → | 100% |
| Errors caught | — | **15/15 (100%)** |
| False positives | — | 0 |

Full methodology: [`benchmarking/benchmark-report-v4-3judge.md`](benchmarking/benchmark-report-v4-3judge.md)

---

## Pipeline

```
User Query
  ↓
[Phase 0] Dedup Gate — emergency skip + content check
  ↓
[Phase 0.5] Pre-answer — extract claims, time-sensitive = force search
  ↓
LLM Response
  ↓
[Phase 1] SIFT — source attribution (✅ source / ⚠️ guessed / ❌ contradiction)
  ↓
[Phase 2] CoVe + FIRE — independent cross-verification, ≥2 sources
  ↓
[Phase 3] FABLE — impact grading (🔴 Critical / 🟡 Experience / 🟢 Cosmetic)
  ↓
[Phase 4] Truth Sandwich — structured correction delivery
```

Key design rules:
- Each phase does ONE thing. Never search AND judge in the same round.
- Time-sensitive items (prices, hours, schedules) force external search.
- Emergency bypass for time-sensitive user scenarios.
- Multi-agent parallel execution when ≥15 claims need verification.

---

## Architecture

The Double-Check system has **two layers** — portable methodology + Hermes-native enforcement.

### Layer 1: SKILL.md (Portable)

The methodology document at `skill/SKILL.md` is pure prompt. Works as system context on any LLM-based agent:

| Platform | How to load |
|:---------|:------------|
| **Claude Code** | Add to project, reference in `CLAUDE.md` |
| **OpenClaw / Cursor** | Import as custom skill or system prompt |
| **ChatGPT / Claude.ai** | Paste Phase 0.5 steps as custom instructions |
| **Any API** | Prepend to system message |

The pipeline (SIFT → CoVe+FIRE → FABLE → Truth Sandwich) is framework-agnostic — no code changes needed to use it as guidance.

### Layer 2: Hermes Plugin (Automatic)

The Python plugin at `plugin/` uses Hermes-specific lifecycle hooks:

| Hook | What it does | API |
|:-----|:-------------|:----|
| `pre_llm_call` | Detect factual questions → inject context | Hermes lifecycle hook |
| `transform_llm_output` | Check dense responses for factual claims | Hermes output hook |
| `ctx.llm.complete()` | Classify question type (fact/theory/tool-use) | Hermes context API |
| `delegate_task` | Spawn sub-agents for deep verification | Hermes sub-agent system |

**Key design: Plugin is orchestrator, not worker.** It only detects and delegates — the actual verification runs in a sub-agent. This keeps the plugin at ~100 lines and lets the sub-agent use all available tools (search, browser, terminal).

### Running on Other Agents

To get automatic verification on a non-Hermes agent:

| Effort | Method | Result |
|:-------|:-------|:-------|
| **Low** | Load SKILL.md as system prompt prefix | Manual pre-check, no code |
| **Medium** | Wrap agent calls in a Python script | Auto pre-answer + post-answer |
| **High** | Implement lifecycle hooks on your platform | Full auto enforcement |

Minimal Python wrapper example:

```python
import openai

def safe_answer(user_query):
    with open("skill/SKILL.md") as f:
        skill = f.read()
    system = skill + "\n\nFollow Phase 0.5 before answering."
    return openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user_query}]
    )
```

---

## Case Studies

### Camino de Santiago Planning
- Round 1: 23 ⚠️ (guessed addresses/prices), 55 ✅ (source confirmed)
- Round 2: 4 wrong addresses + 6 wrong prices/times found
- Round 3: 1 🔴 (Correos Sunday closure → break Madrid plans), 6 🟡, 3 🟢
- **9% → 0% error rate**

### AI Foldable Phone Research
- 44 claims verified across 6 rounds
- Price errors: Nillkin ¥200→¥500, Poetic $23→$59
- Feature hallucination: BOW HB199 touchpad (doesn't exist)
- **9% → 3% → 0% error rate**

---

## Academic Foundations

### Journalism Standards (10)
| Framework | Core | Used In |
|:----------|:-----|:--------|
| **SIFT** | Stop → Investigate → Find Better → Trace | Phase 1 |
| **IFCN** | ≥2 independent sources, nonpartisan transparency | Phase 2 |
| **Truth Sandwich** | Claim → Error → Correction → Source | Phase 4 |
| **IMVAIN** | Independent / Multiple / Verifies / Authoritative / Named | Phase 1 |

### LLM Verification Research (12)
| Framework | Core Insight | Used In | Source |
|:----------|:-------------|:--------|:-------|
| **CoVe** | Draft → Plan questions → Answer independently → Revise | Phase 2 | Meta, 2023 |
| **FIRE** | Atomic claims → Iterative retrieval → Verify → Refine | Phase 2 | ACL 2025 |
| **FABLE** | Functional / Actionable / Blocking / Likelihood / Effort | Phase 3 | HCI 2025 |
| **VeriChain** | Decompose + Verifier Agent + dynamic loop | Architecture | OpenReview 2026 |
| **FLICC** | Fake experts / Logical fallacies / Cherry picking | Logic check | Nature Sci Rep 2024 |

Full framework reference: [`verification-frameworks.md`](references/verification-frameworks.md)

---

## Trade-offs: Journalism vs Academia

Researched against actual papers (June 2026).

| Dimension | 📰 Journalism | 🧠 LLM Academic | Our Hybrid |
|:----------|:------------:|:--------------:|:--:|
| **Core mechanism** | Lateral reading > close reading | Independent answering > self-Q&A | Both |
| **Automation** | ❌ Manual | ✅ Agent-native | Agent-native |
| **Adversarial adapt.** | ❌ Public frameworks targeted | ✅ Doesn't rely on single method | ✅ 2 sources minimum |
| **Motivated reasoning** | ⚠️ Aware, can't solve | ❌ Not studied | ⚠️ Ceiling — unsolved |
| **Empirical base** | Classroom/community | Benchmark datasets | Both + production data |

---

## Pitfalls

### 🐙 Don't Fabricate Numbers
"Reasonable" guesses are almost always wrong. Octopus protein: guessed 15g, actual 29.8g (USDA).

### ⚠️ Dual-Source Contamination
Tour brochure ≠ user's actual booking. Round 1 must tag *intended* source (user vs document), not just *literal* source.

### 💰 1688 Wholesale ≠ Retail
Same item: 1688 ¥15-30 / Taobao ¥50-80 / Amazon $23-60. Always check ≥3 platforms.

### 📊 Don't Mix GPU Benchmarks
Community scores vary by thermals, firmware, ambient temp. Use GSMArena review page 4 or Notebookcheck.

### ⏰ Yesterday's Source May Be Wrong
Time-sensitive items always need current verification. Correos Santiago: opened 7 days in 2024, but 2025 sources still say "closed Sundays."

---

## Quick Start

```bash
# Hermes Agent users
cp -r skill/ ~/.hermes/skills/double-check/
cp -r plugin/ ~/.hermes/plugins/double-check/
hermes skill enable double-check
hermes plugin enable double-check

# Any LLM framework
# Load skill as system prompt + plugin as function call
```

---

## Benchmarking

Full test set and methodology in [`benchmarking/`](benchmarking/):

- [`benchmark-report-v4-3judge.md`](benchmarking/benchmark-report-v4-3judge.md) — 40-question × 3-judge benchmark (+35pp catch rate)
- [`benchmark-test-set.md`](benchmarking/benchmark-test-set.md) — 40 questions across 4 categories
- [`human-arbitration-sheet.md`](benchmarking/human-arbitration-sheet.md) — 3 disputed questions requiring human judgment
- [`test-results-v2.md`](benchmarking/test-results-v2.md) — raw LLM vs auto-verify vs full pipeline comparison

---

## License

MIT © 2026 Harry (Onezion)
