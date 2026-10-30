"""多轮对话管理器。

`DialogueManager` 是系统的编排核心，把一次用户输入串成完整闭环：
  文本解析 → （可选）触发视觉/语音感知 → 意图识别 → 轻量推理 → 回复

- 维护会话历史（最近 N 轮），支持上下文续接；
- 感知与引擎均为注入式，便于替换为更强的实现；
- 纯标准库可运行。
"""

from __future__ import annotations

from collections import deque
from typing import List, Optional

from ..perception import TextPerceiver
from ..perception.vision import PerceptionEvent
from ..engine import IntentRecognizer, RuleReasoner
from .output import OutputFormatter

# 指令前缀 → 触发的感知模态
_VISION_PREFIXES = ("看到", "识别", "看下", "look", "see")
_AUDIO_PREFIXES = ("听到", "听下", "听", "listen", "hear")


class DialogueManager:
    """多轮对话编排器。"""

    def __init__(
        self,
        text: Optional[TextPerceiver] = None,
        recognizer: Optional[IntentRecognizer] = None,
        reasoner: Optional[RuleReasoner] = None,
        formatter: Optional[OutputFormatter] = None,
        history_size: int = 10,
    ):
        self.text = text or TextPerceiver()
        self.recognizer = recognizer or IntentRecognizer()
        self.reasoner = reasoner or RuleReasoner()
        self.formatter = formatter or OutputFormatter()
        self.history: deque = deque(maxlen=history_size)

    def turn(self, user_input: str) -> dict:
        """处理一轮用户输入，返回结构化结果。"""
        # 1) 解析指令，触发对应感知
        events: List[PerceptionEvent] = []
        target = self._extract_target(user_input)

        text_event = self.text.analyze(user_input)
        events.append(text_event)

        modal = self._detect_modal(user_input)
        if modal == "vision" and target:
            events.append(self._vision().analyze_image(target, source="指令触发的视觉感知"))
        elif modal == "audio" and target:
            events.append(self._audio().analyze_wav(target, source="指令触发的语音感知"))

        # 2) 意图识别（融合所有模态）
        intent = self.recognizer.recognize(events)

        # 3) 轻量推理生成回复
        reply = self.reasoner.reply(intent)

        # 4) 记录会话历史
        self.history.append({"user": user_input, "assistant": reply,
                             "intent": intent.name, "modal": modal})

        return self.formatter.format(user_input, reply, intent, modal)

    # ---- 辅助 ----
    def _detect_modal(self, user_input: str) -> Optional[str]:
        text = user_input.lower()
        if any(p in text for p in _VISION_PREFIXES):
            return "vision"
        if any(p in text for p in _AUDIO_PREFIXES):
            return "audio"
        return None

    @staticmethod
    def _extract_target(user_input: str) -> Optional[str]:
        """从指令中抽取文件路径（尝试取最后一个含分隔符/扩展名的片段）。"""
        tokens = user_input.split()
        for t in reversed(tokens):
            if "/" in t or "." in t:
                return t
        return None

    @staticmethod
    def _vision():
        from ..perception.vision import VisionPerceiver
        return VisionPerceiver()

    @staticmethod
    def _audio():
        from ..perception.audio import AudioPerceiver
        return AudioPerceiver()
