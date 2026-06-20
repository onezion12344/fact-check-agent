# Framework Tradeoffs — Journalism vs LLM Academic

> Why fact-check uses a hybrid: SIFT + Truth Sandwich (journalism) for source audit and correction, CoVe + FIRE (academic) for automated verification. Researched June 2026, verified against actual papers.

## 📰 Journalism Frameworks

### Strengths

| Framework | What it does well | Evidence |
|:--|:--|:--|
| **SIFT** (Caulfield 2019) | Lateral reading — open new tabs to check the source, not vertical read. Wineburg et al. found this is the #1 differentiator between pro fact-checkers and ordinary readers. | University studies: SIFT-taught students significantly better at identifying front groups and funding sources vs CRAAP test |
| **Truth Sandwich** | Structured correction format reduces defensiveness: "What was said → What's wrong → Correct info → Source → Action" | Journalist field guide, used by 170+ IFCN certified orgs |
| **IFCN ≥2 independent sources** | Conservative floor standard for any factual claim | Poynter Institute |
| **IMVAIN** | Independent/Multiple/Verifies/Authoritative/Named — multi-dimensional source quality check | Stony Brook Journalism School |

### Weaknesses

| Issue | Detail | Source |
|:--|:--|:--|
| **Adversarial adaptation** | Widely-known frameworks can be defeated by sophisticated actors building interlinked pseudo-independent sites. Lateral reading sees "multiple reports" from a fake network. | DataField.dev case study on SIFT in higher ed |
| **Depth problem** | Produces competent information consumers (know *what* to do) not critically aware citizens (know *why* info ecosystem is structured this way) | Scholar critiques cited in DataField SIFT analysis |
| **Motivated reasoning** | SIFT's "Stop" interrupts habitual sharing but NOT emotionally-driven sharing. Most politically consequential misinformation circulates because people *want* it to be true. | Pennycook & Rand (2019) |
| **No automation** | Purely human workflow. Cannot scale to LLM output verification. | Inherent design limitation |

## 🧠 LLM Academic Frameworks

### Strengths

| Framework | What it does well | Evidence |
|:--|:--|:--|
| **CoVe** (Meta 2023) | Decoupled verification — answering verification questions without seeing the original draft prevents initial hallucination from contaminating the fix. Core insight for Round 2. | Dhuliawala et al. 2023 — reduces hallucination across list-based QA, MultiSpanQA, long-form |
| **FIRE** (ACL 2025 Findings) | Confidence-driven iterative search — only searches when uncertain. LLM cost 7.6× lower, search cost 16.5× lower vs FacTool/Factcheck-GPT with same/better accuracy. | Xie et al. 2025 — tested on FacTool-QA, FELM-WK, BingCheck |
| **VeriChain** (OpenReview 2026) | Multi-agent: decompose → verifier agent → dynamic loop | Not yet independently replicated |
| **TRUST** (arXiv 2026) | 4-agent pipeline: Extract → Retrieve → Verify → Explain | Not yet independently replicated |

### Weaknesses

| Issue | Detail | Source |
|:--|:--|:--|
| **Verification accuracy still imperfect** | CoVe's own paper: "verification questions achieve higher accuracy than original queries, but remain imperfect." The system can check the wrong thing and be confidently wrong about it. | CoVe paper, Remark 9 |
| **Question generation quality is the bottleneck** | CoVe's effect entirely depends on whether the skeptic phase generates good verification questions. Bad questions → bad verification. | CoVe paper |
| **Over-strict reasoning** | LLMs can be too strict — labeling "FUN Word-Cross Puzzle" as false because evidence says "Word-Cross Puzzle" (exact match mismatch). Human fact-checkers use semantic alignment. | FIRE error analysis, Table 8 |
| **Cost scales linearly** | Each claim needs O(n) LLM calls. But mitigated: FIRE confirms most claims (90%+) don't need search. | FIRE ablation: Fire (No Search) vs full |
| **Benchmark quality issues** | 44/135 failed cases in FIRE's study were dataset errors — wrong gold labels, ungrounded claims. | FIRE Table 8: FELM-WK had 12 "not a claim" + 10 false gold labels |
| **Doesn't address motivated reasoning** | Academic frameworks only check output against reference. They don't study why users believe false claims. | Inherent to approach |

## 🏗️ What Each Round Borrows and Why

| Round | Source | Why that source wins |
|:--|:--|:--|
| **Round 0** (Dedup) | Custom | No academic or journalism framework addresses dedup. Practical addition. |
| **Phase 0.5** (Pre-answer) | Custom + FIRE hybrid | FIRE's confidence-driven approach extended to pre-verification of user's question. |
| **Round 1** (SIFT) | Journalism | SIFT is the only framework that distinguishes "what was in the source" from "what I inferred." CoVe/FIRE jump straight to external verification without this audit step. |
| **Round 2** (External verify) | CoVe + FIRE + IFCN | CoVe's decoupled answering + FIRE's iterative search + IFCN's ≥2 sources = minimal search for maximal accuracy. |
| **Round 3** (Impact) | FABLE (HCI 2025) | FABLE's 5-dimension taxonomy (Functional/Actionable/Blocking/Likelihood/Effort) is the right granularity for user decisions. No other framework has this. |
| **Round 4** (Correction) | Truth Sandwich | Journalism's correction format handles user psychology. No academic framework addresses how to present corrections. |

## Key Takeaways

1. **Journalism frameworks are better at WHY** (source motivation, human psychology, correction format) but can't scale.
2. **Academic frameworks are better at HOW** (automated verification, cost optimization, iterative search) but ignore why the user needs verification.
3. **Unsolved by both**: Motivated reasoning — users believing what they want to believe — remains unaddressed by either tradition.
4. **Most practical finding**: FIRE's "most claims don't need search" validates Phase 0.5's split design — "must-search" items (prices, hours, schedules, addresses) vs "internal-knowledge-first" items (product specs, historical facts).
