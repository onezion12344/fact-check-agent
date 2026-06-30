"""
Double-Check v2.0 — Formatting utilities only.
Verification work is delegated to sub-agents via delegate_task.
"""

import time

def format_truth_sandwich(errors: list[dict]) -> str:
    """Format as Truth Sandwich correction block."""
    if not errors:
        return ""

    parts = ["📋 **Fact-Check Verification Results**\n"]

    for severity in ("critical", "experience", "cosmetic"):
        items = [e for e in errors if e.get("severity") == severity]
        if not items:
            continue
        label = {"critical": "🔴 May need correction:", "experience": "🟡 Consider reviewing:", "cosmetic": "🟢 Minor:"}
        parts.append(label[severity])
        for e in items:
            parts.append(f"• {e.get('what_was_written', '')}")
            if e.get("correction"):
                parts.append(f"  → {e['correction']}")
            if e.get("source"):
                parts.append(f"  Source: {e['source']}")
        parts.append("")

    return "\n".join(parts)


def format_verification_context(results: list[dict]) -> str:
    """Format verification results as context injection for the LLM."""
    if not results:
        return ""

    lines = ["【Fact-Check Pre-verification】"]
    for r in results:
        tag = r.get("status", "?")
        claim = r.get("claim", "")
        correct = r.get("correct", "")
        note = r.get("note", "")
        sources = r.get("sources", [])

        tag_map = {"✅": "✅", "⚡": "⚡ 有争议", "❓": "❓ 查不到", "❌": "❌ 错", "⚠️": "⚠️ 未验证"}
        lines.append(f"{tag_map.get(tag, tag)}: **{claim}**")
        if correct:
            lines.append(f"   → 正确: {correct}")
        if note:
            lines.append(f"   → {note}")
        for s in sources[:2]:
            lines.append(f"   → [{s.get('title','')}]({s.get('url','')})")

    lines.append("\n使用以上验证结果回答。❌ 不重复错误说法。❓ 诚报未查到。")
    return "\n".join(lines)


def format_verify_tool_output(results: list[dict]) -> str:
    """Format verification results for tool output."""
    if not results:
        return ""

    summary = {"✅": 0, "⚡": 0, "❓": 0, "❌": 0, "⚠️": 0}
    for r in results:
        s = r.get("status", "⚠️")
        summary[s] = summary.get(s, 0) + 1

    lines = [
        "═══════════════════════════════════════",
        "  Fact-Check Verification Results",
        f"  ✅ {summary.get('✅',0)} ⚡ {summary.get('⚡',0)} ❓ {summary.get('❓',0)} ❌ {summary.get('❌',0)}",
        "═══════════════════════════════════════\n",
    ]

    for r in results:
        tag = r.get("status", "⚠️")
        claim = r.get("claim", "")
        correct = r.get("correct", "")
        note = r.get("note", "")
        sources = r.get("sources", [])

        tag_label = {"✅": "✅ 确认", "⚡": "⚡ 争议", "❓": "❓ 未查", "❌": "❌ 错误", "⚠️": "⚠️ 未验"}.get(tag, tag)
        lines.append(f"{tag_label}: **{claim}**")
        if correct:
            lines.append(f"   → Correct: {correct}")
        if note:
            lines.append(f"   → {note}")
        for s in sources[:2]:
            lines.append(f"   → [{s.get('title','')}]({s.get('url','')})")
        lines.append("")

    return "\n".join(lines)


def create_diagnostic_report(claims: list[str], results: list[dict], duration_ms: int) -> dict:
    """Create structured diagnostic report for logging."""
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "claims_count": len(claims),
        "duration_ms": duration_ms,
        "summary": {s: sum(1 for r in results if r.get("status") == s) for s in ["✅", "⚡", "❓", "❌", "⚠️"]},
    }
