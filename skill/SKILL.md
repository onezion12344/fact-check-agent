---
name: fact-check
description: "Pre-answer 预核查 + Post-answer 四轮递进事实核查。合并 SIFT/CoVe/FIRE/FABLE/IFCN 学术框架。"
version: 1.1.0
---

# 四轮递进事实核查

> 合并新闻界 (SIFT/IMVAIN/IFCN) + LLM 学术界 (CoVe/FIRE/VeriFact) + 多 Agent (VeriChain/TRUST) 最佳实践。
> 核心原则：每轮降维，不一锅炖。

## 📚 学术参考

本技能合并 12 篇学术论文 + 10 个新闻标准 + 9 个 AI 验证系统。
完整框架列表、引用和关键洞见 → `skill_view("fact-check", "references/verification-frameworks.md")`
→ 关键：CoVe (Meta 2023), FIRE (ACL 2025), SIFT (Caulfield 2019), IFCN 标准, FABLE (HCI 2025)

## Reference Files

- `references/foldable-phone-matrix.md` — Verified specs for Find N2/N3/N5/N6/OnePlus Open/Z Fold 7 (GSMArena + manufacturer verified)
- `references/root-matrix.md` — Bootloader unlock status by brand and OS version (XDA + DroidWin verified)
- `references/price-corrections.md` — Known price errors and their corrections from AI Foldable research
- `references/verification-frameworks.md` — Full academic framework reference list
- `references/framework-tradeoffs.md` — Journalism vs LLM Academic: strengths, weaknesses, and why each round borrows from which tradition (researched against actual papers June 2026)
- `references/plugin-architecture.md` — Hermes Plugin implementation: hooks, tools, search engine, and how Plugin + Skill complement each other

## Hermes Plugin (External Implementation)

This skill's methodology is also packaged as a **native Hermes Plugin** at `~/.hermes/plugins/fact-check/`. The Plugin handles **always-on** verification (every turn via `pre_llm_call` + `transform_llm_output` hooks). This skill handles **deep audit** (full Round 1-4 with multi-agent parallelization). They share the same methodology and academic frameworks.

| Component | Location |
|:----------|:---------|
| Plugin files | `~/.hermes/plugins/fact-check/` |
| GitHub repo | `onezion12344/fact-check-agent` |
| Plugin docs | `skill_view("fact-check", "references/plugin-architecture.md")` |

**When to use which:** Enable the Plugin for zero-effort pre-answer checks on every turn. Load this skill (`/skill fact-check`) when the user asks for deep multi-round verification or when you need to run the full SIFT → CoVe+FIRE → FABLE → Truth Sandwich pipeline.

## 触发条件（两种模式）

| 模式 | 触发时机 | 触发条件 | 做什么 |
|:--|:--|:--|:--|
| **Phase 0.5**（Pre-answer 预核查） | **回答前** | 用户问题含事实主张（价格/时间/地址/名称/数值） | 先搜≥2源验证，再回答 |
| **Round 1-4**（Post-answer 后核查） | **回复后** | 回复≥300字且含≥5个具体主张 | 完整四轮（SIFT→CoVe+FIRE→FABLE→Truth Sandwich） |

**选择规则**：
- 用户问 "XX多少钱 / XX地址 / XX几点关门 / XX怎么样" → **Phase 0.5**
- 我已经发了长回复且含大量事实 → **Round 1-4**
- 两者都满足（用户问事实问题+我打算发长回复）→ **先 Phase 0.5 验证 → 回答 → 如果回答密集再补 Round 1-4**

**触发粒度**：仅主 Agent 启动。子 Agent (delegate_task) 不自动启动技能 — 它们的核查结果由主 Agent 在第 3-4 轮汇总。

## ⛔ 第 0 轮 — 去重门（跑之前先检查）

**目的**: 防止同一内容被多个 Agent 重复核查。同时在用户处于紧急场景时跳过。

```
急停检查：
  用户是否在时间敏感场景？
    → 正在餐厅点菜 / 手机快没电 / 路上缺水 / 迷路 / 找巴士
    → YES: 回答紧急问题。DEFER fact-check。标注 "第 0 轮: 紧急场景延后"
    → NO: 继续去重门

去重检查：
  1. 检查上下文: 这条内容已经被核查过了吗？
     → 搜索本轮对话中的 "第 4 轮" / "Truth Sandwich" / "核查报告"
     → 搜索本轮对话中的 "Phase 0.5" / "Pre-answer 预核查"
  2. 如果已有完整结果: 直接用。不重跑。
  3. 从中断点继续。
  4. 没有: 进入 Phase 0.5（如果用户问题含事实主张）或 Round 1-4（如果是我刚发了长回复）
```

**判断标准**: 同一个内容对象只跑一次 Phase 0.5。内容变了（新事实、新主张）才算新核查。

**并行场景**: 如果主 Agent 决定用 delegate_task 加速外验（Phase 0.5 或 Round 2），子 Agent 只做验证部分，不做完整流程。主 Agent 收到结果后继续。

## 🔍 Phase 0.5 — Pre-answer 预核查（新增）

**目的**: 在回答用户之前，先核实问题中涉及的事实主张。防止基于错误假设回答问题。

**触发**：紧接第 0 轮之后判断。如果用户问题**不包含**事实主张（纯闲聊/问意见/问概念），跳过，直接正常回答。

### 步骤

```
Step 1 - 提取用户问题中的事实主张：
  扫描用户问题，提取所有事实性实体
  → 价格: "XX 多少钱" "预算 XX" "XX 要花多少"
  → 时间: "几点关门" "什么时候出发" "XX 多久"
  → 地址/位置: "XX 在哪" "怎么去 XX"
  → 名称: "XX 是什么牌子" "XX 好不好" (含产品/店家/地名)
  → 数值: "几公里" "多大" "多少"

  输出: 待验证主张列表（每条标注类别: 价格/时间/地址/名称/数值）

Step 2 - 分两组处理：
  第一组 - 时效敏感项（强制外验，不依赖内部知识）：
    → 价格、营业时间、时刻表、地址
    → 这些必须 web_search，不能用记忆或猜测
    → 至少搜索 2 个独立来源

  第二组 - 通用事实项（可先用内部知识，不确定再搜）：
    → 产品参数、历史事实、名称确认
    → 先用内部知识判断
    → 置信度低时 -> web_search 补充
    → 置信度高 -> 直接采用（FIRE 论文验证了大部分 claim 不需要搜）

Step 3 - 并行搜索（时效敏感项优先）：
  对第一组：立即并行 web_search ≥2 源（用 batch_search 或多个搜索调用）
  对第二组：置信度低时才触发搜索

  搜索要求：
  - 每条搜索独立，不参考我的原始回答（CoVe 原则）
  - ≥2 个独立来源（IFCN 标准）
  - 检查不同平台/角度，不重复搜同一个来源

Step 4 - 合成验证结果（四类状态）：
  ✅ 基本正确 — ≥2 独立来源一致确认
  ⚡ 有争议 — 来源之间有矛盾，或独立来源不足（如只搜到同一家媒体的多篇文章）
  ❓ 查不到 — 搜了但没找到相关信息。❓≠❌，不要把它当证据说"不存在"
  ❌ 错 — 来源明确反驳该主张

  ⚠️ 未外验 — 非时效敏感项，仅用 LLM 内部知识（需注意：LLM 内部知识可能过时或有误）

Step 5 - 基于验证结果回答问题：
  使用已验证的信息作答
  对 ✅ 项：直接使用，可标注来源
  对 ⚡ 项：在回答中明确标注争议："XX 的说法存在争议，不同来源说法不一"
  对 ❓ 项：诚实说"没有查到可靠信息"——不要用查不到来暗示"所以它是错的"
  对 ❌ 项：不要重复错误说法，直接给出正确的
```

### 输出规范

回答时，对已验证的事实主张采用行内标注：

```
OnePlus Open 闲鱼约 ¥2,400✅（BDtheBear 2026.06，2源确认）
Nillkin 键盘约 ¥460❓（搜了一圈没找到统一报价，Amazon $79.99 但淘宝 ¥430-500，渠道差大）
Correos 周日关门✅（官网确认）
行李转运服务 ⚡（搜到 2 家，评价两极分化，无法判断哪家可靠）
```

**四类状态回答指南：**
- ✅ 标注来源，直接回答
- ⚡ 说明分歧："说法A vs 说法B，目前没有定论"
- ❓ 诚实说"没查到"——不要用❓当证据
- ❌ 纠正但不重复错误："这个说法不对，实际是XX"

### 答后补充

如果 Phase 0.5 后的回答 ≥300 字且含 ≥5 个主张 → 继续走 **第 1-4 轮** 作为补充杀（backstop）。此时第 1 轮的 SIFT 需要把 Phase 0.5 验证过的内容标记为 ✅（已确认），只对新增/未验证的主张做 ⚠️ 标记。

### 不自查场景

- 纯主观问题："哪家好吃" "哪个好看" → 跳过，不需要验证
- 概念解释："什么是 RAG" "量子纠缠是什么" → 跳过 Phase 0.5，直接回答
- 用户明确说"你看看这个"给我文件/URL → 使用 Round 1-4 流程（SIFT 对照），不需要 Phase 0.5
- 紧急场景（第 0 轮已跳过）→ 直接回答

## 第 1 轮 — SIFT 源码对照

**目的**: 区分「原文有的」和「我补的」，不做外部搜索。

```
Stop: 暂停，不信任刚写的内容
Source: 每条主张标注来源
  - ✅ 引用源: km 标记、教堂名 → 逐字对照
  - ⚠️ 推理补全: 价格、地址、营业时间 → 标记为"需外验"
  - ❌ 矛盾: 原文说 X，我写了 Y
Trace: 追溯不在原文里的 → 它们从哪来的？(之前搜索/记忆/推测)
```

输出: **缺口清单** — ✅ ⚠️ ❌ 三类，不越界去做外验。

## 第 2 轮 — CoVe+FIRE 交叉验证

**目的**: 对第 1 轮的 ⚠️ 和随机抽 20% 的 ✅ 做外部验证。

```
CoVe (Chain-of-Verification):
  生成验证问题: "这个地址对吗？" "这个价格对吗？"
  独立回答: 不参考我原来的内容，用新搜索的结果回答

FIRE (Iterative Retrieval):
  搜索 → 不满足 → 再搜 → 直到证据收敛
  每条 ⚠️ 主张 ≥2 个独立源 (IFCN 标准)

时效敏感项强制外验:
  - 营业时间 (最容易变)
  - 价格 (次容易变)  
  - 时刻表 (再容易变)
  - 地址/场馆 (基础设施可能搬迁 — 如 Santiago 巴士站 2021 年已搬)
  这四个不依赖原文 — 原文可能是几年前的。
```

输出: **验证清单** — 每条主张: 确认 ✅ / 修正 🔧 / 矛盾但原文正确 ⚡

## 第 3 轮 — FABLE 影响分析

**目的**: 修正后的错误哪些真的影响决策？不查新东西。

```
FABLE:
  Functional? — 这个修复功能上需要吗？
  Actionable? — 会改变用户做什么吗？
  Blocking? — 不修会打断关键路径吗？
  Likelihood? — 用户遇到这个错误的概率多大？
  Effort? — 修起来成本多大？

三级:
  🔴 Critical Path: 不修会打断行程 (如: 周日取不了行李)
  🟡 Experience: 修了更好但不打断 (如: 餐厅地址错一条街)
  🟢 Cosmetic: 纯文字修正 (如: 酒店名字格式)
```

输出: **分级修复清单** + 替代方案 (对 🔴 必须给方案)

## 第 4 轮 — Truth Sandwich 修正

**目的**: 结构化输出修正，给用户上下文。

```
Truth Sandwich:
  1. What was written (原话)
  2. What's wrong (为什么错)
  3. What's correct (正确是什么)
  4. Source (来源)
  5. Action needed? (需要改变行程吗？)
```

---

## 实例：Camino Notion 核查

- 第 1 轮: 发现 23 条 ⚠️ (我补的地址/价格), 55 条 ✅ (原文有的 km/教堂)
- 第 2 轮: 23 条 ⚠️ 外部验证, 发现 4 个地址错 + 6 个价/时间错
- 第 3 轮: 1 个 🔴 (Correos 周日关门打断 Madrid), 6 个 🟡, 3 个 🟢
- 第 4 轮: Truth Sandwich 修正所有 + 替代方案

## 实例：AI Foldable 手机/配件核查 (2026.06)

### 六轮核查历程
- 第 1 轮: 44 条 ✅ 37 / ⚠️ 3 / ❌ 4（价格全偏低 2-2.6× — Nillkin ¥200实为¥500, Logitech ¥350实为¥620, Poetic $23实为$59）
- 第 2-3 轮: 新增 21 条 → 65 总条 / ✅ 53 / ⚠️ 10 / ❌ 2（BOW HB199 无触控板, GPU 数据从社区抄的→GSMArena验证）
- 第 4-6 轮: 持续更新 Notion 页面 + 修正 SIM 规格 / eSIM / 典藏版 / 系统版本细节
- 错误率趋势: 9% → 3% → 0% 残余

### 手机配件价格陷阱（新增）
- **1688 批发价 ≠ 个人零售价**: 同一个壳 1688 ¥15-30, 淘宝 ¥50-80, Amazon $23-60
- **同一商品多平台价差可达 2-3×**: Nillkin 官方 $69.99, Amazon US $79.99, Amazon UK £49.99(~$63)
- **永远同时查 ≥3 个平台**: 淘宝/京东/拼多多 + Amazon + 官方商店
- **二手/闲鱼价格**: 无法自动化验证 — 标记为"估算"，不列为确定数据

### GPU 基准陷阱（新增）
- GSMArena 的 3DMark Wild Life Extreme 数据 = 可信 (N3: 4,529-4,588)
- 社区/YouTube 跑分 = 不可信 — 环境温度/调频策略/固件版本差异太大
- 不要混用 onscreen 和 offscreen 数字 (如 GFXBench Car Chase onscreen N2=59fps，但我错误地引用了 104fps offscreen)
- 来源统一: GSMArena review page 4 (有完整图表) + Notebookcheck UL Solutions 数据

### OPPO Pen 技术陷阱（新增）
- 52audio 拆解: OPPO Pen = Goodix GP850 主动电容笔，不依赖 EMR 数位板层
- OPPO 官方兼容列表 (opposhop.cn): 仅 Find N2/N3/N5/OnePlus Open
- 普通手机不支持 — 触控控制器需固件支持 USI/HPP 笔协议

---

## 注意事项

- ⛔ **旅行手册/团行程 ≠ 用户实际预订。** 永远优先取用户 app 截图的酒店名、CI 时间、价格。团体行程表只是参考，不是真相。Camino 案例：UMSL 团住 VILLAJARDÍN，Harry 自己定 Pons Minea——用错了会导致整个路线计划报废。
- 第 1 轮禁止外部搜索 — 只对照原文
- 第 2 轮不判断影响 — 只验证
- 第 3 轮不搜索 — 只分析已验证结果
- 每轮必须有不同的输出格式，防止混在一起
- **回答完当前问题再开新话题。** Harry 说 "回答完" — 意思是完成当前回答，不要把答案和下一步混在一起。尤其是路上紧急场景（点菜、找路）

### ⛔ 第 1 轮前置要求：保存源文本

在启动核查前，必须已提取并保存原文全文。若源文本未提取或已从上下文驱逐：
1. 重新提取原文 (web_extract / mcp_anysearch_extract)
2. 完整保存为本地 temp 文件以便逐行对照
3. 才开始第 1 轮

无源文本的 SIFT 是盲人摸象。不要依赖上下文摘要——摘要会遗漏关键细节。

### 域特定 vs 结构轮次（不要混淆）

❌ 错误：三个 agent 按域分（住宿/路线/餐馆）→ 本质是同一方法跑三次
✅ 正确：三个 agent 按结构轮次分（SIFT源码对照 / 外验 / 影响分析）→ 每轮降维

域特定分块仅适用于**并行加速**（第 2 轮大量外验时），不适用于轮次本身。

### 并行子 Agent 核查模式（仅用于加速第 2 轮外验）

当第 2 轮外验量很大时（≥15 条 ⚠️ 主张），可并行 2-3 个子 Agent **同时做外验**（不是做不同轮次）。每个子 Agent 都遵循 fact-check 第 2 轮方法论。

⚠️ 这是**横向分块**（加速），不是轮次替代。第 1、3、4 轮仍然由主 Agent 串行执行。

### 分块策略
```python
delegate_task(tasks=[
  {goal: fact-check phone specs + root claims,  toolsets: ["web","terminal","skills"]},
  {goal: fact-check accessories + prices,       toolsets: ["web","terminal","skills"]},
  {goal: fact-check performance + features,     toolsets: ["web","terminal","skills"]}
])
```

### 每个子 Agent 的 task context 必须包含
1. `Load skill_view(name='fact-check') first` — 让子 Agent 遵循 4 轮方法论
2. 具体的子主张列表（逐条列出要核查的内容）
3. 要求结构化输出：✅ 确认 / ⚠️ 偏误 / ❌ 错误 + 修正值 + 来源

### 价格核查要点
- 价格是最常见错误源。不要依赖记忆或估算。
- 实际查验时：搜索平台名 + 商品名 → 提取当前价格 → 标注币种和日期
- 二手/优惠价格 ≠ 当前零售价。明确标注来源平台和是否为促销价。
- 例：Nillkin Cube Pocket — 第一次说 ¥200（是记忆/批发价），实际 Amazon $79.99（2026.06）

### 常见陷阱
- 文章/评测里的价格可能是过时价或首发价，不等于当前价
- 同一商品在不同平台（Amazon/淘宝/京东）价差可达 2×
- 国内渠道（1688/拼多多）价低但有起批量限制，个人不一定能买到
- 🐙 **餐厅菜单/营养数据不可编造**：不要说 "他们有 empanada" 除非你查到了菜单。不要说 "章鱼蛋白 15g" — 实际是 29.8g（USDA）。编造的"合理数字"几乎总是错的。
- ⚠️ **双源污染 (Dual-Source Contamination)**：当同一话题有两个不同来源时，必须区分哪个对哪个是权威的。案例：Camino 规划时，UMSL 学生团小册子对教堂名/km 是权威来源，但对用户的酒店预订完全不是——用户自己在 Booking.com 定的。第 1 轮必须标注每条主张的*意图*来源（这个信息应该来自用户还是文档？），不只是*字面*来源。用户已确认的信息（Booking 截图、日历事件）比公开文档优先级更高。
- ⚠️ **⚠️ 来源外标记是 SIFT 的灵魂**：第 1 轮最有价值的输出不是 ✅ 和 ❌，而是 ⚠️——你补的内容。这些是第 2 轮外验的靶子。不要跳过它们，不要觉得"合理的补全"无所谓。这次 Camino 核查中，酒店名字全错但教堂名字全对——因为酒店是你补的（未标注），教堂是原文有的。如果第 1 轮把酒店标记为 ⚠️，第 2 轮外验就能纠正。
