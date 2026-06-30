# Tool Use Verification — Industry Landscape (2026.06.30)

> Structured taxonomy of 20+ papers/tools across 6 routes (A–F), identifying the single verified gap: **post-hoc tool selection correctness verification**.

## 6-Route Taxonomy

```
Route A — 什么时候该调用工具 (决策层)
Route B — 工具是否允许调用 (安全/权限层)
Route C — 工具选择偏差分析 (分析层)
Route D — 工具链规划 (规划层)
Route E — 工具调用效率/冗余检测 (运行时层)
Route F — 工具选择自验证 (selection-time层)

空白 — 执行后回头看：已经调了的工具对不对
        → Post-hoc Tool Selection Correctness Verification
```

---

## Route A: When to Call (Decision Layer)

**Core question:** Model calls tools when it shouldn't. Waste of tokens/cost.

### Papers

| Paper | Venue | Institution | Key insight | Key data |
|-------|-------|-------------|-------------|----------|
| SMART (arXiv 2502.11435) | ACL 2025 Findings | — | Metacognitive training reduces tool overuse | -24% tool use, +37% accuracy; 7B matches GPT-4o |
| Metis/HDPO (arXiv 2604.08545) | — | Alibaba | Hierarchical decoupled policy optimization | Redundant calls 98% → 2% |
| To Call or Not to Call (arXiv 2605.00737) | Preprint (Jun 2026) | MPII | Decision-theoretic framework: necessity/utility/affordability. Hidden state estimators align perceived vs true need | Model-perceived need frequently misaligned with true need; estimator-driven controller improves decisions |
| Tool-Overuse Illusion (arXiv 2604.19749) | Preprint (Mar 2026) | — | Knowledge epistemic illusion: models misjudge internal knowledge boundaries. Outcome-only rewards inadvertently encourage overuse | Knowledge-aware DOP reduces tool use 82.8% with accuracy gain; balanced reward cuts unnecessary calls 66.7% (7B), 60.7% (32B) |
| Entropy & Tool-Use | ACL 2026 | — | Role of entropy in optimizing tool-use behaviors | — |

### What this route does NOT cover

All train/policy-level — teaches model when NOT to call. Does NOT verify whether a call that was made was the right tool.

---

## Route B: Tool Permissions (Safety/Policy Layer)

**Core question:** Called tool has too much privilege. Safety/security risk.

### Papers/Tools

| Paper/Tool | Venue | Key insight | Key data |
|------------|-------|-------------|----------|
| AgentSpec (arXiv 2503.18666) | ICSE 2026 | Lightweight DSL runtime constraints | <5ms/eval |
| Veto (veto.so) | 2026 | Deterministic external policy engine, 7-param May judgment | Determinism = 1.0 |
| Edictum (edictum.ai) | 2026 | Open-source runtime governance library | Allow/block/approve/log |
| ABC (arXiv 2602.22302) | — | Agent Behavior Contracts: (P)recondition (I)nvariant (G)overnance (R)ecovery | Formal guarantee |
| AGT | Microsoft (Apr 2026) | 7-pkg governance toolkit, MIT | Covers OWASP Agentic Top 10 |
| Probity (github.com/nizos/probity) | 2026 | Coding agent process discipline | Agent hook system |
| Over-Privileged Tool Selection (arXiv 2606.20023) | Preprint (Jun 2026) | ToolPrivBench: 544 scenarios × 8 domains × 5 risk patterns. Tests if agents choose higher-privilege tools when lower suffices | Qwen3-8B 64.9% OPUR, LLaMA-3.1-8B 55.9%; 6/11 models ≥30%; Claude 4.6 Sonnet/GPT-5.2/GLM-5 <10%. Transient failures amplify escalation significantly |
| Quantitative Certification (arXiv 2510.03992) | — | Formal certification of tool selection robustness | Robustness guarantees under adversarial perturbations |

### Key finding from Over-Privileged Tool Selection paper

GPT-5.2 zero-shot bias: 5 times at PED=0 → 13 at PED=1 → 35 at PED=2. Transient failures cause escalation. General safety alignment (AgentAlign) does NOT reliably transfer to least-privilege tool selection — post-training targeted at privilege awareness needed.

### What this route does NOT cover

Checks privilege level, not optimal tool choice. A low-privilege tool could still be the wrong tool for the task.

---

## Route C: Tool Selection Bias (Analysis Layer)

**Core question:** Why does the model pick one tool over another?

### Papers

| Paper | Venue | Key insight | Key data |
|-------|-------|-------------|----------|
| BiasBusters (arXiv 2510.00307) | ICLR 2026 (Oxford/Torch/OpenAI) | Systematic tool selection bias: models fixate on one provider or favor contextually earlier tools. (1) Semantic alignment is primary driver; (2) Small perturbations to tool descriptions shift choices; (3) Pre-training exposure amplifies bias | 7 LLMs evaluated; certain APIs selected 10x more often; mitigation: filter + uniform sampling |
| Tool Selection Bias | OpenReview | Similar, more metadata-level | — |

### What this route does NOT cover

Analysis-only. Does not provide runtime verification or correction.

---

## Route D: Tool Chain Planning (Planning Layer)

**Core question:** What's the optimal sequence of tools for a multi-step task?

### Papers

| Paper | Venue | Key insight |
|-------|-------|-------------|
| Feasible is Not Enough | ACL 2026 Findings | Cost-aware optimal tool-chain planning on multi-solution tool graphs. Acknowledges multiple valid solutions → pick lowest cost |
| ToolTree | ICLR 2026 | MCTS dual-feedback planning + bidirectional pruning. Training-free plug-and-play module |
| AutoTool | AAAI 2026 | Graph-based lightweight tool selection framework to reduce inference overhead |

### What this route does NOT cover

Pre-execution planning only. Does not verify execution-time tool choices.

---

## Route E: Tool Call Efficiency / Runtime Guards

**Core question:** Is the agent making redundant or inefficient tool calls?

### Papers/Tools

| Source | Key insight | Key data |
|--------|-------------|----------|
| Tool Spam (agentpatterns.tech, 2026) | 4 redundancy patterns: repeated signature, argument jitter, retry amplification, fan-out spam | Case: 1 task → 52 calls / 6min / ~$3 vs normal ~$0.10 |
| MLflow ToolCallEfficiency (Dec 2025) | Agentic Judge detecting redundant/inefficient calls via LLM-as-Judge | 5 inefficient + 5 efficient test cases published |
| Session-Scoped Deduplication (dev.to) | Session-level tool+args_hash dedup | Prevents same tool+args from firing twice |
| ToolCallCorrectness (MLflow companion) | Judge: does tool call correctly address user intent? | — |

### What this route does NOT cover

Detects **same tool repeated** — not "a different tool would have been better." A tool called once can still be the wrong tool.

---

## Route F: Tool Selection Self-Verification (Selection-Time)

**Core question:** Did I pick the right tool right now?

### Papers

| Paper | Venue | Key insight | Key data |
|-------|-------|-------------|----------|
| ToolVerifier (arXiv 2402.14158) | Meta (Feb 2024) | Self-verification during tool selection: self-ask contrastive questions to distinguish close candidates. Covers tool selection AND parameter generation | ToolBench 4 tasks / 17 unseen tools; avg +22% over few-shot baselines |

### Why this is NOT sufficient

ToolVerifier is **selection-time** — it questions the tool choice while the LLM is making it. It is NOT **post-hoc** — it does not look back at an already-executed call and verify optimality against ALL available tools.

---

## THE VERIFIED GAP: Post-Hoc Tool Selection Correctness

```
After agent called tool_X(args) — verify:
  1. Was there a cheaper/faster alternative achieving the same goal?
  2. Did this call create redundancy (info already obtainable from prior calls)?
  3. Would a tool COMBINATION be better than the single tool chosen?
  4. Was the tool over-privileged (more access than needed)?
  5. Was the tool over-scoped (did more than the problem requires)?

No published work covers any of these 5 dimensions post-hoc.
ToolVerifier (Route F) is the closest but its timing is selection-time.
Over-Privileged Tool Selection (Route B) confirms the problem exists
  but does not build a verifier.
```

---

## Benchmarks

| Benchmark | Coverage | Leader |
|-----------|----------|--------|
| BFCL V4 | Function calling correctness | GLM-5.1: 77.5 |
| MCP-Atlas | 36 servers / 220 tools / 1000 tasks | Gemini 3.5 Flash: 83.6% pass |
| ToolPrivBench (Jun 2026) | 544 scenarios × 8 domains × 5 risk patterns | Over-privilege measurement only |

---

## Source Attribution

This landscape was compiled via multi-source search (AnySearch + arXiv + GitHub + Unite.AI) on 2026.06.30. Each paper's abstract was extracted from the original arXiv/ACL/OpenReview page. No paper was read in full — claims are based on published abstracts and public summaries. Verify specific numbers against the full paper before citing.
