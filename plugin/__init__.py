"""
Double-Check Plugin v2.0 — Hermes Agent.

Hybrid: LLM classify → inject delegate instruction → sub-agent does deep verification.
No regex pattern matching. No built-in search engine. Plugin is orchestrator, not worker.

Hooks:
  - pre_llm_call: Classify question → inject delegate_task instruction for sub-agent
  - transform_llm_output: Detect dense factual response → inject post-check instruction

Three pillars:
  - Fact: prices, times, addresses, specs, numbers
  - Theory: logic, reasoning, concept validation
  - Tool Use: tool selection auditing
"""

import json
import logging
import re
import os
import urllib.request
import urllib.error

logger = logging.getLogger("plugins.double-check")

# ── Cheap router model (auto-discovered on first load) ──
_ROUTER_MODEL = None  # e.g. "free-trial/gpt-3.5-turbo"
_ROUTER_API_KEY = None
_ROUTER_BASE = "https://openrouter.ai/api/v1"
_ROUTER_DISCOVERED = False

def _discover_router():
    """Try to find a free/cheap model for routing. Runs once on plugin load."""
    global _ROUTER_MODEL, _ROUTER_API_KEY, _ROUTER_DISCOVERED
    if _ROUTER_DISCOVERED:
        return
    _ROUTER_DISCOVERED = True

    # 1. Try OpenRouter key from env or Hermes config path
    for key_name in ["OPENROUTER_API_KEY", "OPENAI_API_KEY"]:
        k = os.environ.get(key_name)
        if k:
            _ROUTER_API_KEY = k
            break
    if not _ROUTER_API_KEY:
        # Try reading from Hermes config
        try:
            config_path = os.path.expanduser("~/.hermes/config.yaml")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    for line in f:
                        if "openrouter" in line.lower() and "api_key" in line.lower():
                            parts = line.split(":")
                            if len(parts) >= 2:
                                _ROUTER_API_KEY = parts[1].strip().strip('"').strip("'")
                                break
        except Exception:
            pass

    if not _ROUTER_API_KEY:
        logger.info("No router API key found — using main model for classify")
        return

    # 2. Fetch free models from OpenRouter
    try:
        req = urllib.request.Request(f"{_ROUTER_BASE}/models")
        req.add_header("Authorization", f"Bearer {_ROUTER_API_KEY}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        # Find free models, prefer fastest (smallest context)
        free_models = []
        for m in data.get("data", []):
            pricing = m.get("pricing", {})
            prompt_price = float(pricing.get("prompt", "1"))
            completion_price = float(pricing.get("completion", "1"))
            if prompt_price == 0 and completion_price == 0:
                name = m["id"]
                ctx = m.get("context_length", 0)
                free_models.append((name, ctx))

        if not free_models:
            # Try models with very low price instead
            for m in data.get("data", []):
                pricing = m.get("pricing", {})
                prompt_price = float(pricing.get("prompt", "1"))
                if prompt_price < 0.0001:  # <$0.10/M tokens
                    name = m["id"]
                    ctx = m.get("context_length", 0)
                    free_models.append((name, ctx))

        if free_models:
            # Sort by context length ascending (smaller = faster)
            free_models.sort(key=lambda x: x[1])
            _ROUTER_MODEL = free_models[0][0]
            logger.info(
                "Router model: %s (free, %d ctx, %d candidates)",
                _ROUTER_MODEL, free_models[0][1], len(free_models)
            )
        else:
            logger.info("No free model found on OpenRouter — using main model")
    except Exception as e:
        logger.warning("Router discovery failed: %s — using main model", e)


def _router_complete(prompt: str) -> str:
    """Call the cheap router model. Falls back to ctx.llm.complete pattern."""
    if not _ROUTER_MODEL or not _ROUTER_API_KEY:
        return None  # caller should fall back

    body = json.dumps({
        "model": _ROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 300,
    }).encode()

    req = urllib.request.Request(
        f"{_ROUTER_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {_ROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning("Router call failed: %s", e)
        return None

# Regex gate: skip clearly non-factual messages fast
_GENERAL_PATTERNS = re.compile(
    r"^(hi|hello|hey|thanks|ok|okay|bye|goodbye|yes|no|nope|yep|"
    r"どうも|ありがとう|すみません|おはよう|こんにちは|こんばんは|"
    r"早上好|下午好|晚上好|你好|您好|谢谢|再见|好的|嗯|好的吧|"
    r"明白了|知道了|了|好|行|可以|没问题|随便|看看|"
    r"lol|lmao|nice|great|awesome|cool|wow|omg|wtf|"
    r"test|testing|demo)$",
    re.IGNORECASE,
)

_FACTUAL_TRIGGERS = re.compile(
    r"(价格|多少|多少钱|¥|\$|€|£|成本|费用|预算|"
    r"几点|什么时候|多久|时间|地址|在哪|怎么去|"
    r"参数|规格|配置|尺寸|重量|版本|型号|"
    r"有什么区别|对比|vs|versus|哪个好|推荐|"
    r"怎么|如何|步骤|教程|能不能|是否支持|"
    r"price|cost|how much|when|where|address|"
    r"spec|specs|size|weight|model|version|"
    r"compare|difference|vs|versus|recommend|"
    r"how to|tutorial|steps|does it support)",
    re.IGNORECASE,
)

def _safe_json_parse(raw: str) -> dict | None:
    """Parse JSON from LLM output with tolerance for leading/trailing noise."""
    if not raw:
        return None
    raw = raw.strip()
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try extracting {...} or [...] block
    for delim in ("{", "["):
        start = raw.find(delim)
        if start == -1:
            continue
        end = raw.rfind("}" if delim == "{" else "]")
        if end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                continue
    return None

CLASSIFY_PROMPT = """Analyze this user question and return ONLY a JSON object (no other text):

{
  "question_type": "factual" | "theory" | "tool_use" | "general",
  "claims": ["list of specific factual claims mentioned"],
  "time_sensitive": true | false,
  "confidence": "high" | "medium" | "low"
}

Classification rules:
- factual: asks about prices, times, addresses, specs, numbers, current info, comparisons
- theory: asks about concepts, logic, reasoning, definitions, explanations, differences
- tool_use: asks about how to do something, which tool/method to use
- general: greetings, opinions, subjective, chat, emotional

Extract ALL specific claims (prices, names, numbers, addresses, times) into the claims array.

Question: {question}"""

POST_CHECK_PROMPT = """Does this response contain factual claims that should be verified by a sub-agent?
Return ONLY a JSON object (no other text):

{
  "needs_check": true | false,
  "claim_count": <number of factual claims detected>,
  "reason": "<brief explanation>"
}

Only return needs_check=true if there are at least 3 specific factual claims
(prices, times, numbers, names, locations, specifications).

Response: {response}"""


def _classify(llm_complete, question: str) -> dict:
    """Use regex gate → cheap router LLM → fallback main LLM to classify."""
    # Regex gate 1: pure greeting/acknowledgment — skip entirely
    if _GENERAL_PATTERNS.match(question.strip()):
        return {"question_type": "general", "claims": [], "time_sensitive": False, "confidence": "low"}

    has_factual_trigger = bool(_FACTUAL_TRIGGERS.search(question))

    # Try cheap router model first (faster, cheaper)
    raw = _router_complete(CLASSIFY_PROMPT.format(question=question[:600]))
    if raw:
        result = _safe_json_parse(raw)
        if result and result.get("question_type"):
            return result

    # Fallback: main model
    try:
        raw = llm_complete(CLASSIFY_PROMPT.format(question=question[:600]))
        result = _safe_json_parse(raw)
        if result and result.get("question_type"):
            return result
    except Exception as e:
        logger.warning("Classify LLM call failed: %s", e)

    # Final fallback: regex hint
    if has_factual_trigger:
        logger.info("Classify fallback: regex triggered → factual")
        return {"question_type": "factual", "claims": [question[:200]], "time_sensitive": True, "confidence": "low"}
    return {"question_type": "general", "claims": [], "time_sensitive": False, "confidence": "low"}


def _post_check(llm_complete, response: str) -> dict:
    """Use cheap router model first, fallback main model."""
    # Try cheap router model first
    raw = _router_complete(POST_CHECK_PROMPT.format(response=response[:1000]))
    if raw:
        result = _safe_json_parse(raw)
        if result and "needs_check" in result:
            return result

    # Fallback: main model
    try:
        raw = llm_complete(POST_CHECK_PROMPT.format(response=response[:1000]))
        result = _safe_json_parse(raw)
        if result and "needs_check" in result:
            return result
    except (json.JSONDecodeError, TypeError, Exception) as e:
        logger.warning("Post-check failed: %s", e)
    return {"needs_check": False, "claim_count": 0, "reason": "classification failed"}


def _build_pre_instruction(qtype: str, claims: list, time_sensitive: bool) -> str:
    """Build delegate instruction — forces TWO rounds of sub-agent verification (pre + post)."""
    labels = {"factual": "🔍 事实性", "theory": "🧠 理论/逻辑", "tool_use": "🔧 工具选择"}
    label = labels.get(qtype, "📋")
    emoji = "🔍" if qtype == "factual" else "🧠" if qtype == "theory" else "🔧"

    lines = [
        f"⛔ [DOUBLE-CHECK TRIGGERED — DOUBLE VERIFICATION REQUIRED]",
        f"",
        f"用户问题被 {emoji} Double-Check Plugin 分类为: {label}",
        f"",
        f"### 你的任务 (MANDATORY — TWO ROUNDS 不可跳过):",
        f"",
        f"**第一轮 — 预核查 (PRE-VERIFY):**",
        f"1. 立即调用 `delegate_task` 启动子 agent，在回答用户之前做独立验证",
        f"2. 子 agent 使用 DIFFERENT MODEL (config delegation 指定的) → full web search",
        f"3. 子 agent 返回结构化结果 (✅/⚡/❓/❌ 每条主张)",
        f"4. **把核查结果作为独立消息发送到当前聊天** (用户要在 IM 里看到)",
        f"5. 再回答用户原始问题 — 用已验证的信息作答",
        f"",
        f"**第二轮 — 后验查 (POST-VERIFY, 回答完后自动做):**",
        f"6. 回答完毕后，再用 `delegate_task` 启动另一个子 agent",
        f"7. 子 agent 检查你的回答中的事实主张是否准确",
        f"8. 如有错误 → 用 Truth Sandwich 格式发修正到聊天",
        f"9. 如全部正确 → 发一条 ✅ 确认消息",
        f"",
        f"**⚠️ 注意:**",
        f"- 两轮使用同一个子 agent 不行，必须是两次独立的 `delegate_task` 调用",
        f"- 子 agent 必须用不同的模型 (delegation config 已设置)",
        f"- 子 agent 必须做 web search，不能只靠 LLM 内部知识",
        f"- **用户如果在聊天里看不到核查消息 → 说明你漏了步骤。重做。**",
    ]
    if claims:
        lines.append(f"")
        lines.append(f"### 检测到的事实主张 ({len(claims)} 条):")
        for c in claims[:8]:
            lines.append(f"  - {c}")
    if time_sensitive:
        lines.append("")
        lines.append("⚠️ **包含时效敏感信息** — 必须搜索当前实时数据，不能依赖模型内部知识")

    lines.extend([
        "",
        "### 预核查输出格式 (用户要在 IM 里看到的):",
        "",
        "━━━━━━━━━━━━━━━━━━",
        f"{emoji} Double-Check 预核查 [{qtype.upper()}]",
        "━━━━━━━━━━━━━━━━━━",
        "✅ xxx — 2源确认",
        "⚡ xxx — 来源有分歧",
        "❌ xxx — 实际为 yyy (来源)",
        "━━━━━━━━━━━━━━━━━━",
        "",
        "### 后验输出格式 (回答完后额外发):",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "📋 Double-Check 后验核查",
        "━━━━━━━━━━━━━━━━━━",
        "✅ 全部正确 — 3条主张均已独立验证确认",
        "━━━━━━━━━━━━━━━━━━",
        "",
        "或",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "📋 Double-Check 后验核查 — 发现修正",
        "━━━━━━━━━━━━━━━━━━",
        "❌ xxx → 实际为 yyy (来源)",
        "━━━━━━━━━━━━━━━━━━",
    ])
    return "\n".join(lines)


def _build_post_instruction(claim_count: int) -> str:
    """Build post-answer verification instruction — forces visible check."""
    return "\n".join([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📋 POST-ANSWER Double-Check 验证请求",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"检测到上一轮回答包含约 {claim_count} 个事实主张。",
        "",
        "**你的任务 (MANDATORY):**",
        "1. 用 `delegate_task` 启动子 agent — 对上一轮回答做 SIFT → CoVe+FIRE → FABLE → Truth Sandwich",
        "2. **子 agent 返回后，把核查结果以独立消息发到当前聊天**",
        "3. 对 ✅ 项直接标注，对 ❌ 项做 Truth Sandwich 修正",
        "",
        "输出格式:",
        "━━━━━━━━━━━━━━━━━━",
        "📋 Double-Check 后验核查",
        "━━━━━━━━━━━━━━━━━━",
        "✅ xxx — 已验证",
        "⚡ xxx — 有争议",
        "❌ xxx → 实际为 yyy",
        "━━━━━━━━━━━━━━━━━━",
        "",
        "如果用户没有看到这条核查消息 → 说明你漏了。重做。",
    ])


def register(ctx):
    """Register Double-Check hooks. Auto-discovers cheap router model on load."""
    _discover_router()

    # ═══════════════════════════════════════════════
    # pre_llm_call — Classify → inject delegate
    # ═══════════════════════════════════════════════
    def pre_llm_hook(user_message, is_first_turn, **kwargs):
        if not user_message or len(user_message) < 10:
            return None

        classification = _classify(ctx.llm.complete, user_message)
        qtype = classification.get("question_type", "general")

        if qtype == "general":
            return None

        claims = classification.get("claims", [])
        time_sensitive = classification.get("time_sensitive", False)

        # Theory without specific claims: only trigger if high confidence
        if qtype == "theory" and not claims and classification.get("confidence") != "high":
            return None

        instruction = _build_pre_instruction(qtype, claims, time_sensitive)
        logger.info("Phase 0.5: %s | %d claims | ts=%s", qtype, len(claims), time_sensitive)
        return {"context": instruction}

    ctx.register_hook("pre_llm_call", pre_llm_hook)

    # ═══════════════════════════════════════════════
    # transform_llm_output — Post-check instruction
    # ═══════════════════════════════════════════════
    def transform_output(response_text, **kwargs):
        if not response_text or len(response_text) < 300:
            return None

        result = _post_check(ctx.llm.complete, response_text)
        if not result.get("needs_check"):
            return None

        count = result.get("claim_count", 0)
        if count < 3:
            return None

        logger.info("Post-check: %d claims", count)
        return response_text + _build_post_instruction(count)

    ctx.register_hook("transform_llm_output", transform_output)

    # ═══════════════════════════════════════════════
    # Command: /factcheck
    # ═══════════════════════════════════════════════
    def handle_factcheck(args):
        if args and args.strip():
            target = args.strip()
            nl = "\n"
            return (
                f"🔍 **Double-Check Deep Audit — 已触发**{nl}{nl}"
                f"待核查内容: {target[:200]}...{nl}{nl}"
                f"请执行完整的 4 轮核查:{nl}"
                f"1. SIFT — 源码对照{nl}"
                f"2. CoVe+FIRE — 独立交叉验证 (≥2源){nl}"
                f"3. FABLE — 影响分级 (🔴/🟡/🟢){nl}"
                f"4. Truth Sandwich — 结构化修正{nl}{nl}"
                f"使用 `delegate_task` 启动子 agent 执行全流程。"
            )
        nl = "\n"
        router_info = f"Router: {_ROUTER_MODEL or 'main model (no free model found)'}"
        return (
            f"🔍 **Double-Check v2.1 — Active**{nl}{nl}"
            f"{router_info}{nl}"
            f"自动检测问题类型 → delegate 子 agent 验证 → 返回验证结果。{nl}{nl}"
            f"三大支柱:{nl}"
            f"  • 🔍 Fact — 事实性主张验证 (CoVe+FIRE+IFCN){nl}"
            f"  • 🧠 Theory — 逻辑/推理验证 (FLICC+Toulmin+FoVer){nl}"
            f"  • 🔧 Tool Use — 工具选择审计 (6-路线分类 + post-hoc){nl}{nl}"
            f"子 agent 执行全量搜索 + 交叉验证 + 结构化返回。{nl}{nl}"
            f"用法:{nl}"
            f"  /factcheck — 显示状态{nl}"
            f"  /factcheck &lt;text&gt; — 对指定内容执行深度 4 轮审计"
        )

    ctx.register_command(
        name="factcheck",
        handler=handle_factcheck,
        description="Show Double-Check v2.0 status",
    )

    logger.info(
        "Double-Check Plugin v2.1 loaded — router=%s, regex gate + 3-pillar classify",
        _ROUTER_MODEL or "main-model",
    )
