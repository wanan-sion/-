"""文本感知模块。

职责：
- 输入归一化（去空白、统一大小写）；
- 关键词/意图信号抽取（命中词表即标记）；
- 输出 `PerceptionEvent(modal="text", ...)`。

默认实现为纯规则、零依赖；可被替换为 TF-IDF / 向量检索等轻量语义方案。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .vision import PerceptionEvent

# 轻量意图信号词表：命中的词将写入 payload["signals"]
_INTENT_SIGNALS = {
    "greeting": ["你好", "hi", "hello", "在吗", "嗨"],
    "status": ["状态", "健康", "status", "汇报", "报告"],
    "vision_query": ["看到", "识别", "图片", "图像", "画面", "look", "see"],
    "audio_query": ["听到", "语音", "音频", "声音", "listen", "hear"],
    "help": ["帮助", "help", "怎么用", "功能"],
    "quit": ["退出", "再见", "quit", "exit", "拜拜"],
}


class TextPerceiver:
    """轻量文本感知器。"""

    def __init__(self):
        self._stopwords = {"的", "了", "和", "与", "是", "在", "吗", "呢", "啊"}

    def normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def analyze(self, text: str, source: str = "用户输入") -> PerceptionEvent:
        norm = self.normalize(text)
        signals = {
            intent: [w for w in words if w in norm]
            for intent, words in _INTENT_SIGNALS.items()
        }
        signals = {k: v for k, v in signals.items() if v}
        return PerceptionEvent(
            modal="text", source=source,
            payload={"text": text, "normalized": norm, "signals": signals,
                     "length": len(text)},
            confidence=1.0,
        )
