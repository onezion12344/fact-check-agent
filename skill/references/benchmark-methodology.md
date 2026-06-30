# Benchmark Methodology — LLM Factual Accuracy Testing

> Created 2026-06-23 from 40-question DeepSeek V4 Flash benchmark.
> Use this to benchmark any LLM's raw factual accuracy vs accuracy with Double-Check pipeline.

## Test Design

### 40 Questions × 4 Categories

| Category | Focus | # Questions | Why This Matters |
|:---------|:------|:-----------:|:-----------------|
| A: Prices | Product costs, subscriptions, retail | 10 | LLMs consistently guess low — worst category |
| B: Specs | Hardware specs, features, dimensions | 10 | GPU gen confusion, feature hallucination |
| C: Stats | Populations, percentages, counts | 10 | "Reasonable" numbers fabricated |
| D: Schedules | Hours, dates, seasonal info | 10 | Cultural generalizations, stale data |

### Question Design Principles

1. **Pick topics where LLMs historically hallucinate**: brand names, current prices, geopolitical stats
2. **Include both easy and hard questions**: some should be obvious (ChatGPT Plus = $20) to catch false positives
3. **Mix time-sensitive and stable facts**: prices change weekly, GPU models don't
4. **Avoid obscure trivia**: every question should be something a reasonable user would actually ask

### Running the Benchmark

```
Step 1 — Raw baseline:
  For each of 40 questions:
    - Ask the model directly (no verification)
    - Record the answer verbatim
    - Mark: ✅ correct / ❌ wrong / ⚡ stale / ❓ source-dep

Step 2 — Double-Check pipeline:
  Same 40 questions, but with Phase 0.5 + Rounds 1-4 active
  Record:
    - Which errors the pipeline caught
    - Which correct answers it passed (false positives = 0 target)
    - Tool calls per answer (cost metric)

Step 3 — Compute:
    Raw accuracy = correct / total
    Pipeline accuracy = (correct after correction) / total
    Δ = pipeline accuracy - raw accuracy
    Error catch rate = errors caught / total errors committed
```

## Error Type Taxonomy

From actual testing across 40 questions on DeepSeek V4 Flash:

| Error Type | Frequency | Category Hotspots | Root Cause |
|:-----------|:---------:|:------------------|:-----------|
| **Price underestimation** | 20% | A (Prices) | LLM guesses low-end or wholesale prices |
| **Price overestimation** | 7% | A | Currency/region confusion |
| **GPU gen confusion** | 7% | B (Specs) | Adreno 730 vs 740 — same chip family |
| **Feature hallucination** | 7% | B | LLM "assumes" logical features (touchpad) |
| **Screen size undershoot** | 7% | B | Foldable displays guessed too small |
| **Numerical fabrication** | 13% | C (Stats) | "Reasonable"-sounding numbers invented |
| **Popular metric inflation** | 7% | C | MAUs, trust %s inflated |
| **Stale geopolitical data** | 7% | C | Recognition counts, borders outdated |
| **Cultural generalization** | 7% | D (Schedules) | "Spain = Sunday closure" stereotype |
| **Seasonal assumption** | 7% | D | "Hostels close in winter" — wrong |
| **Hours rounded** | 7% | D | Precise times rounded to convenient numbers |
| **Count off by 1-2** | 7% | C | UNESCO sites, members — off by small margin |

## Category-Level Patterns

| Category | Raw Accuracy | Why So Low |
|:---------|:-----------:|:-----------|
| A: Prices | **50%** | LLM uses cached launch prices or guesses Chinese wholesale |
| B: Specs | **80%** | Best category — specs change slowly, well-documented |
| C: Stats | **50%** | LLM fabricates "reasonable" numbers; geopolitical data goes stale |
| D: Schedules | **70%** | Cultural generalizations; seasonal info assumed wrong |

## Typical Results

DeepSeek V4 Flash (2026-06-23):
- Raw accuracy: **62.5%** (25/40)
- Pipeline accuracy: **97.5%** (39/40)
- Δ improvement: **+35 pp**
- Error catch rate: **100%** (15/15)
- False positives: **0**
- Stale truth detected: **2 cases**

## Extending to Other Models

To test DeepSeek V4 Pro or any other model:
1. Use the same 40-question test set
2. Run via the target model's API
3. Record raw answers
4. Run Double-Check pipeline
5. Compare Δ

Expected: stronger models (V4 Pro) will have lower raw error rate (~20-25% vs 37.5%) but still benefit from pipeline for time-sensitive items.
