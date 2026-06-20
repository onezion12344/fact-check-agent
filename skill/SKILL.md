name: fact-check
description: "Pre-answer 预核查 + Post-answer 四轮递进事实核查。合并 SIFT/CoVe/FIRE/FABLE/IFCN 学术框架。"
version: 1.1.0
---

# 四轮递进事实核查

> 合并新闻界 (SIFT/IMVAIN/IFCN) + LLM 学术界 (CoVe/FIRE/VeriFact) + 多 Agent (VeriChain/TRUST) 最佳实践。
> 核心原则：每轮降维，不一锅炖。

## 触发条件（两种模式）

| 模式 | 触发时机 | 触发条件 | 做什么 |
|:--|:--|:--|:--|
| **Phase 0.5**（Pre-answer 预核查） | **回答前** | 用户问题含事实主张（价格/时间/地址/名称/数值） | 先搜≥2源验证，再回答 |
| **Round 1-4**（Post-answer 后核查） | **回复后** | 回复≥300字且含≥5个具体主张 | 完整四轮（SIFT→CoVe+FIRE→FABLE→Truth Sandwich） |

**选择规则**：
- 用户问 "XX多少钱 / XX地址 / XX几点关门 / XX怎么样" → **Phase 0.5**
- 我已经发了长回复且含大量事实 → **Round 1-4**
- 两者都满足（用户问事实问题+我打算发长回复）→ **先 Phase 0.5 验证 → 回答 → 如果回答密集再补 Round 1-4**

## 第 0 轮 — 去重门

**目的**: 防止同一内容被多个 Agent 重复核查。同时在用户处于紧急场景时跳过。

```
急停检查：
  用户是否在时间敏感场景？
    → 正在餐厅点菜 / 手机快没电 / 路上缺水 / 迷路 / 找巴士
    → YES: 回答紧急问题。DEFER

去重检查：
  1. 检查上下文: 这条内容已经被核查过了吗？
  2. 如果已有完整结果: 直接用。不重跑。
  3. 没有: 进入 Phase 0.5 或 Round 1-4
```

## Phase 0.5 — Pre-answer 预核查

**目的**: 在回答用户之前，先核实问题中涉及的事实主张。

### 步骤

```
Step 1 - 提取用户问题中的事实主张：
  → 价格、时间、地址/位置、名称、数值

Step 2 - 分两组处理：
  第一组 - 时效敏感项（强制外验）：
    → 价格、营业时间、时刻表、地址
    → 至少搜索 2 个独立来源
  第二组 - 通用事实项：
    → 先用内部知识判断
    → 置信度低时 -> web_search 补充

Step 3 - 并行搜索
  - 每条搜索独立（CoVe 原则）
  - ≥2 个独立来源（IFCN 标准）

Step 4 - 合成验证结果：
  ✅ 确认  🔧 修正  ⚡ 争议  ❌ 无法验证

Step 5 - 基于验证结果回答问题
```

### 输出规范

```
OnePlus Open 闲鱼约 ¥2,400✅（2源确认）
Nillkin 键盘约 ¥460🔧（之前说¥350，实际¥430-500）
```

### 不自查场景

- 纯主观问题、概念解释、用户给文件/URL、紧急场景

## 第 1 轮 — SIFT 源码对照

**目的**: 区分「原文有的」和「我补的」，不做外部搜索。

```
Source: 每条主张标注来源
  - ✅ 引用源: km 标记、教堂名 → 逐字对照
  - ⚠️ 推理补全: 价格、地址、营业时间 → 标记为"需外验"
  - ❌ 矛盾: 原文说 X，我写了 Y
```

输出: **缺口清单** — ✅ ⚠️ ❌ 三类

## 第 2 轮 — CoVe+FIRE 交叉验证

**目的**: 对第 1 轮的 ⚠️ 做外部验证。

```
CoVe: 生成验证问题 → 独立回答（不参考原文）
FIRE: 搜索 → 不满足 → 再搜 → 直到证据收敛
IFCN: 每条 ⚠️ 主张 ≥2 个独立源

时效敏感项强制外验:
  - 营业时间、价格、时刻表、地址
```

## 第 3 轮 — FABLE 影响分析

```
🔴 Critical Path: 不修会打断行程
🟡 Experience: 修了更好但不打断
🟢 Cosmetic: 纯文字修正
```

## 第 4 轮 — Truth Sandwich 修正

1. What was written（原话）
2. What's wrong（为什么错）
3. What's correct（正确是什么 + 来源）
4. Action needed?（需要改变行程吗？）

## 学术参考

完整框架列表：参见 `references/verification-frameworks.md`

关键框架：
- SIFT (Caulfield 2019) — 新闻来源评估
- CoVe (Meta 2023) — Chain-of-Verification
- FIRE (ACL 2025) — 迭代检索验证
- FABLE (HCI 2025) — 影响分析
- IFCN — ≥2 独立源标准
- VeriFact-CoT, VeriChain, TRUST, GKMAD — 多 Agent 验证

## 常见陷阱

- 🐙 **不可编造数据**：不要编造合理的数字
- ⚠️ **双源污染**：区分意图来源和字面来源
- 💰 **价格平台差异**：1688≠零售，查≥3平台
- 📊 **GPU基准**：只用 GSMArena + Notebookcheck
- 🖊️ **OPPO Pen**：仅特定机型支持
