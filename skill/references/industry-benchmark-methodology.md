# Industry Benchmark Methodologies for LLM Factuality

> Research compiled 2026-06-25 during Double-Check benchmark redesign.
> Enriched 2026-06-26 with architectural details and practical applicability analysis.

---

## Three Approaches

### 1. SimpleQA (OpenAI, Oct 2024)

| Dimension | Detail |
|:----------|:-------|
| **Dataset** | 4,326 short fact-seeking questions across history, science, tech, art, entertainment |
| **Ground Truth** | Human-annotated. Every question has ONE answer that doesn't change over time. |
| **Judge** | NO LLM. Model output vs human ground truth → exact string match. |
| **Metric** | accuracy = correct / (correct + incorrect + not attempted) |
| **Key Limitation** | Answers must be time-invariant. Excludes prices, schedules, current data — exact scenarios Double-Check is built for. |
| **How it breaks the LLM-judge cycle** | Avoids it entirely. Human answers are gold. |

**Open-source variant:** SimpleQA Verified (arXiv 2509.07968, Sep 2025) — 1,000-prompt curated subset addressing label noise and topical bias.

### 2. FACTS Grounding (Google DeepMind, Dec 2024)

| Dimension | Detail |
|:----------|:-------|
| **Dataset** | 1,719 long-form examples (860 public + 859 held-out). Each: document (up to 32K tokens) + system instruction + user request. Domains: finance, tech, retail, medicine, law. |
| **Judge** | 3 frontier LLMs: **Gemini 1.5 Pro**, **GPT-4o**, **Claude 3.5 Sonnet** |
| **Calibration** | Judges validated against held-out test set to find best-judging prompt templates. Verified agreement with human raters. |
| **Two-phase** | (1) Eligibility check — did the model address the user request? (2) Factual grounding — is every claim attributable to the source document? |
| **Scoring** | Average of all 3 judge models' scores across all examples. |
| **Paper** | <https://arxiv.org/abs/2501.03200> |

**Critical quote from the DeepMind blog:**
> *"We selected a combination of different judges to mitigate any potential bias of a judge giving higher scores to the responses produced by a member of its own model family."*

**Top models achieve only ~74% accuracy** on FACTS (as of Feb 2026) — underscoring how hard factuality is even with grounded context.

### 3. HHEM — Hughes Hallucination Evaluation Model (Vectara, 2023-2026)

| Dimension | Detail |
|:----------|:-------|
| **Architecture** | Fine-tuned **DeBERTaV3** (not a general LLM). A specialized binary classifier. |
| **Training** | FLAN-T5 XXL generates synthetic training data; DeBERTa fine-tuned for factual consistency (NLI/entailment on source→summary pairs). |
| **Output** | 0.0–1.0 factual consistency score per summary. |
| **Key advantage** | NOT a general LLM — eliminated the "LLM judge LLM" circularity for this specific task. |
| **Key limitation** | Only tests summary→source consistency. Cannot evaluate creative reasoning, logic, or domain synthesis. |
| **Open version** | HHEM-2.1-Open on HuggingFace. Commercial: HHEM-2.3. |

**HHEM fits where you have source→output pairs and want binary consistency.** It does not fit open-ended factual claims where the LLM is guessing from training data, not summarizing a provided document.

---

## Why None of These Fit Double-Check Directly

| Requirement | SimpleQA | FACTS | HHEM |
|:------------|:--------:|:-----:|:----:|
| Price/time verification | ❌ "answers never change" | ❌ no price/time benchmarks | ❌ summary only |
| Logical fallacy detection | ❌ | ❌ | ❌ |
| Pipeline Δ measurement | ❌ measures model, not pipeline | ❌ measures model, not pipeline | ❌ |
| Open-ended factual claims | ❌ short-form only | ✅ context-provided | ❌ |
| Multi-model disagreements transparent | ❌ | ✅ 3-judge | ❌ binary |

**Double-Check's unique challenge:** We're measuring not "how accurate is the model?" but "how much does the pipeline improve accuracy? And how do we measure accuracy for claims where even authoritative sources disagree?"

---

## Practical Decision Guide

| Scenario | Which Method | Why |
|:---------|:------------|:----|
| Measuring pipeline Δ (model vs model+pipeline) | Custom 3-judge panel | No existing benchmark measures pipeline improvement |
| Benchmarking a new model's factuality | SimpleQA (fast, reproducible) | Time-invariant answers, no LLM judge |
| Evaluating long-form grounded responses | FACTS (3-judge + human calibration) | Context-provided, multi-judge reduces bias |
| Detecting hallucination in RAG | HHEM | Binary classifier, fast, open-source |
| Measuring Double-Check's value (our use case) | Custom: human calibration set + multi-judge + disagreement transparency | Acknowledge LLM-as-judge limitations transparently |

---

## Key Takeaway for Double-Check Benchmarks

The three industry approaches each solve part of the problem:

1. **SimpleQA** avoids LLM-as-judge by only asking time-invariant questions → not our domain
2. **FACTS** mitigates LLM bias with 3 judges + human calibration → closest to our methodology
3. **HHEM** uses a specialized small model, not a general LLM → not our task type

**Our approach:** Adopt FACTS' multi-judge + calibration pattern, but acknowledge that for open-ended factual claims (prices, stats, logic), no existing benchmark methodology is a perfect fit. Transparency about limitations is more honest than pretending we've solved LLM-as-judge.
