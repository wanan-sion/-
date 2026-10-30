"""输出格式化器。

把一次交互的结构化结果格式化为：控制台可读文本 / 结构化 dict（供 API 返回）。
"""

from __future__ import annotations

from ..engine.intent import INTENT_LABELS


class OutputFormatter:
    """格式化交互结果。"""

    def format(self, user_input: str, reply: str, intent, modal) -> dict:
        return {
            "user": user_input,
            "intent": intent.name,
            "intent_label": INTENT_LABELS.get(intent.name, intent.name),
            "confidence": round(intent.confidence, 2),
            "modality": modal or "text",
            "reply": reply,
        }

    @staticmethod
    def to_console(result: dict) -> str:
        """控制台友好的展示格式。"""
        lines = [
            f"用户  : {result['user']}",
            f"意图  : {result['intent_label']}（{result['intent']}，置信度 {result['confidence']}）",
            f"模态  : {result['modality']}",
            f"助手  : {result['reply']}",
        ]
        return "\n".join(lines) + "\n" + "-" * 50
