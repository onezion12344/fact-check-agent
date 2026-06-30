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

logger = logging.getLogger("plugins.double-check")

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
    """Use LLM to classify question type and extract claims."""
    try:
        raw = llm_complete(CLASSIFY_PROMPT.format(question=question[:600]))
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError, Exception) as e:
        logger.warning("Classify failed: %s", e)
        return {"question_type": "general", "claims": [], "time_sensitive": False, "confidence": "low"}


def _post_check(llm_complete, response: str) -> dict:
    """Use LLM to check if response needs post-verification."""
    try:
        raw = llm_complete(POST_CHECK_PROMPT.format(response=response[:1000]))
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError, Exception) as e:
        logger.warning("Post-check failed: %s", e)
        return {"needs_check": False, "claim_count": 0, "reason": "classification failed"}


def _build_pre_instruction(qtype: str, claims: list, time_sensitive: bool) -> str:
    """Build delegate instruction injected before LLM answers."""
    labels = {"factual": "🔍 事实性", "theory": "🧠 理论/逻辑", "tool_use": "🔧 工具选择"}
    label = labels.get(qtype, "📋")

    lines = [
        f"{label} **问题检测 — 需要子 Agent 验证**\n",
        f"类型: {label}",
    ]
    if claims:
        lines.append(f"待验证主张 ({len(claims)} 条):")
        for c in claims[:8]:
            lines.append(f"  • {c}")
    if time_sensitive:
        lines.append("\n⚠️ **包含时效敏感信息** — 必须搜索当前实时数据")
    lines.extend([
        "\n**请在回答前执行:**",
        "1. 调用 `delegate_task` 启动子 agent",
        "2. 子 agent: 全量搜索 → 交叉验证 ≥2 源 → 结构化返回",
        "3. 等子 agent 返回后，用验证结果回答",
        "4. 每个主张标注来源",
    ])
    return "\n".join(lines)


def _build_post_instruction(claim_count: int) -> str:
    """Build post-answer verification instruction."""
    return (
        "\n\n📋 **Post-Answer 验证请求**\n\n"
        f"检测到 {claim_count} 个事实主张。\n"
        "请对上一轮回答执行:\n"
        "1. `delegate_task` → 子 agent 做 SIFT → CoVe+FIRE → FABLE → Truth Sandwich\n"
        "2. 返回修正并追加"
    )


def register(ctx):
    """Register Double-Check hooks."""

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
        return (
            "🔍 **Double-Check v2.0 — Active**\n\n"
            "自动检测问题类型 → delegate 子 agent 验证 → 返回验证结果。\n\n"
            "三大支柱:\n"
            "  • 🔍 Fact — 事实性主张验证\n"
            "  • 🧠 Theory — 逻辑/推理验证\n"
            "  • 🔧 Tool Use — 工具选择审计\n\n"
            "子 agent 执行全量搜索 + 交叉验证 + 结构化返回。"
        )

    ctx.register_command(
        name="factcheck",
        handler=handle_factcheck,
        description="Show Double-Check v2.0 status",
    )

    logger.info("Double-Check Plugin v2.0 loaded — LLM classify + delegate pattern")
