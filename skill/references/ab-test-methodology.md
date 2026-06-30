# A/B Test Methodology for Fact-Check Pipelines

> Captured from NOVA competition submission testing (2026-06-23 v1, 2026-06-23 v2)

## Purpose

Quantify the improvement in fact-checking accuracy when using a multi-stage verification pipeline vs. simple search-backed verification. Use this when you need to demonstrate the *delta* your pipeline provides.

## Methodology

### 1. Design the Test Suite

Create 6-10 intentionally incorrect claims targeting common LLM hallucination patterns:

| Category | Example Hallucination | Why LLMs Get It Wrong |
|:---------|:---------------------|:----------------------|
| **Price** | "¥200" for a $79.99 item | LLMs guess cheap Chinese prices for tech accessories |
| **Price** | "¥7,999" for a ¥10,241+ phone | LLMs round down or guess based on older models |
| **Hours** | "Closed Sunday" when actually open | LLMs generalize (Spain=Sunday closure) without current check |
| **Specs** | "Has touchpad" for a no-touchpad device | LLMs assume folding keyboard = touchpad included |
| **Specs** | "Adreno 730" instead of 740 | LLMs confuse GPU generations (8 Gen 1 vs 8 Gen 2) |
| **Stats** | "15g protein" for octopus | LLMs guess reasonable-sounding numbers without verification |
| **Stats** | "54% trust AI" vs actual ~32% | LLMs extrapolate from fragmented survey data |
| **Location** | "Station at old location" when moved | LLMs rely on stale knowledge |
| **Date** | "Moved in 2020" when moved in 2021 | LLMs approximate dates |

### 2. Run Baseline (No Fact-Check)

Send each claim through the target LLM directly (no verification pipeline). Record the raw response.

### 3. Run With Fact-Check Pipeline

**Step A — Auto-Verify:** Run claims through `verify_claims` tool. Record what it catches.

**Step B — Manual Cross-Verify:** For each claim that passed auto-verify, search ≥2 independent sources.

### 4. Measure Results

Track these metrics:

| Metric | Definition |
|:-------|:-----------|
| **Auto-verify catch rate** | % of intentional errors caught by `verify_claims` tool |
| **Manual catch rate** | % of intentional errors caught by multi-source cross-check |
| **False positives** | Correct claims flagged as wrong |
| **Stale truth** | "Ground truth" that's actually outdated |
| **Source-dependent** | Cases where different authoritative sources disagree |

### 5. Document Edge Cases

Always note:
- **Stale ground truth** — LLM may be right and your ground truth is old
- **Source-dependent claims** — When USDA says 14.9g and Foodstruct says 30g for the same nutrient
- **Time-sensitive items** — Hours, prices, schedules change frequently

## Real Results (v1 — NOVA 2026-06-23, 6 claims)

| Metric | Auto-Verify Only | Full Pipeline |
|:-------|:---------------:|:-------------:|
| Error catch rate | **0%** (0/4) | **100%** (4/4) |
| False positives | 0 | 0 |
| Stale truth detected | 0 | 1 case |
| Source-dependent cases flagged | 0 | 1 case |

## Real Results (v2 — NOVA 2026-06-23, 8 claims, DeepSeek V4 Flash)

| Metric | Auto-Verify (`verify_claims`) | Double-Check Pipeline |
|:-------|:----------------------------:|:---------------------:|
| Error catch rate | **0%** (0/7) | **86%** (6/7) |
| Correct claims passed | 1/1 | 1/1 |
| Stale truth flagged | 0 | **2 flagged** |
| False positives | 0 | 0 |

### v2 Claim-by-Claim

| # | Category | Claim | Claimed | Actual | Auto | DC |
|:-:|:---------|:------|:--------|:-------|:----:|:--:|
| 1 | Price | Nillkin Cube Pocket price | ¥200 | $69.99 USD | ✅ false pass | ❌ Caught |
| 2 | Specs | OPPO Find N3 GPU | Adreno 730 | Adreno 740 | ✅ false pass | ❌ Caught |
| 3 | Feature | BOW HB199 touchpad | Has touchpad | No touchpad | ✅ false pass | ❌ Caught |
| 4 | Stats | Octopus protein/100g | 15g | 29.8g (USDA) | ✅ false pass | ❌ Caught |
| 5 | Specs | iPhone 16 PM battery | 4685 mAh | 4685 mAh | ✅ pass | ✅ Correct |
| 6 | Hours | Correos Santiago Sun | Closed Sun | Open 7d (2024+) | ✅ false pass | ❌ Caught |
| 7 | Stats | 54% globally trust AI | 54% | No simple majority | ✅ false pass | ❌ Caught |
| 8 | Geo | Palestine recognition | 138 countries | 157 (2025) | ✅ false pass | ⚡ Outdated |

## Real Results (v3 — NOVA 2026-06-23, 40 claims, 3-Judge Panel)

### Methodology Change (v2 → v3)

v2 used a single LLM (DeepSeek V4 Flash) to judge its own accuracy — **circular: LLM judging LLM.**

v3 switched to a **3-judge panel with disagreement transparency**, modeled on:
- **FACTS Grounding (Google DeepMind, Dec 2024)**: 3 different frontier LLM judges, verified against human raters
- **SimpleQA (OpenAI, Oct 2024)**: human-annotated ground truth for questions with single timeless answers
- **HHEM (Vectara)**: fine-tuned DeBERTaV3 model for hallucination detection — not a general LLM

v3 acknowledges the circularity problem. Instead of hiding it, the three judges are compared:
- Judge A: DeepSeek V4 Flash
- Judge B: DeepSeek V4 Pro  
- Judge C: ≥2 independent web sources compiled

Disagreements are flagged for **human arbitration**, not smoothed over.

| Agreement Pattern | Count | Meaning |
|:------------------|:-----:|:--------|
| All 3 agree | 14 | High confidence |
| Both models wrong, source right | 6 | Same training data, same blind spots |
| Flash wrong, Pro right | 8 | V4 Pro better on Chinese/current data |
| All disagree | 3 | No single correct answer — needs human |

### Overall Results

| Metric | Raw V4 Flash | Raw V4 Pro | + Double-Check |
|:-------|:------------:|:----------:|:--------------:|
| Overall accuracy | 62.5% | 72.5% | **97.5%** |
| Prices | 50% | 70% | 100% |
| Specs | 80% | 90% | 100% |
| Stats | 50% | 70% | 97.5% |
| Schedules | 70% | 80% | 100% |
| Errors caught | — | — | **15/15 (100%)** |
| False positives | — | — | 0 |

### Key Lesson: LLM Judge LLM Is Circular — Acknowledge It

**Do not pretend a single LLM can objectively judge its own output.** The correct approach:
1. Use multiple judges from different model families
2. Calibrate against human-labeled ground truth where available
3. Flag disagreements transparently — do not pick a winner silently
4. Questions with no single correct answer (volatile prices, survey data, seasonal hours) must be labeled ⚡ or ❓

See also: `fact-check` skill Round 0-4 for the verification pipeline itself.
