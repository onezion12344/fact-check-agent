# Benchmark v4 — 3-Judge Panel Results

**Date:** 2026-06-25  
**Models:** DeepSeek V4 Flash → DeepSeek V4 Pro  
**Method:** 3-judge panel (V4 Flash raw / V4 Pro raw / source-verified ground truth) + human arbitration  

## Key Results

| Metric | V4 Flash | V4 Pro | Δ |
|:-------|:--------:|:------:|:--:|
| Overall accuracy raw | 62.5% | 72.5% | +10 pp |
| Prices accuracy | 50% | 70% | +20 pp |
| Specs accuracy | 80% | 90% | +10 pp |
| Stats accuracy | 50% | 70% | +20 pp |
| Schedules accuracy | 70% | 80% | +10 pp |
| With Double-Check | 97.5% | 97.5% | same |

## 3-Judge Agreement Patterns

| Pattern | Count | Meaning |
|:--------|:-----:|:--------|
| AAA= (all agree, correct) | 14 | High confidence |
| AA≠C (both models wrong) | 6 | Same training, same blind spots |
| A≠BB=C (Flash wrong, Pro right) | 8 | Pro better on Chinese pricing |
| B≠AA=C (Pro wrong, Flash right) | 0 | Flash never outperformed Pro |
| A≠B≠C (all disagree) | 1 | Palestine time-decay |
| ⚡ No single correct answer | 3 | Needs human arbitration |

## Shared Blind Spots (6 questions)
Both V4 Flash and V4 Pro got wrong: Nillkin price, GPU model, touchpad, octopus protein, Correos Sunday hours, Greccio hostel winter. Same training data → same errors. Pipeline caught all 6.

## Human Arbitration Needed (3 questions)
- C2: AI trust % — no single global metric exists
- A3: Samsung 990 Pro price — $129-$320 depending on retailer  
- D5: Santiago Cathedral hours — seasonal, conflates access with Mass times
