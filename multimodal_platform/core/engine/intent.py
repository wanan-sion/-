"""意图识别与多模态融合。

把感知层给出的一个或多个 `PerceptionEvent`（可能来自视觉、语音、文本）
融合为单一意图。当前实现：
- 以文本信号的信号词为主要依据，配合模态来源做加权；
- 多模态同时出现时，自动合并为“多模态意图”（例如既看到图像又听到语音）。

这是“智能感知交互”的核心理解入口，可平滑替换为基于轻量 LLM / 规则的更强实现。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..perception.vision import PerceptionEvent


@dataclass
class Intent:
    """识别出的意图。"""

    name: str                 # 意图名
    confidence: float         # 置信度 0~1
    modalities: List[str]     # 参与判定的模态
    signals: dict             # 命中的信号词
    detail: dict              # 附加信息

    def __repr__(self) -> str:  # pragma: no cover
        return (f"Intent({self.name}, conf={self.confidence:.2f}, "
                f"modal={self.modalities}, signals={list(self.signals)})")


# 意图名 -> 中文描述（供 UI/日志使用）
INTENT_LABELS = {
    "greeting": "问候",
    "status": "状态汇报",
    "vision_query": "视觉感知",
    "audio_query": "语音感知",
    "multimodal": "多模态感知",
    "help": "帮助",
    "quit": "退出",
    "unknown": "未识别",
}


class IntentRecognizer:
    """轻量意图识别器（规则 + 多模态融合）。"""

    def __init__(self):
        self._priority = ["quit", "help", "greeting", "vision_query",
                          "audio_query", "status"]

    def recognize(self, events: List[PerceptionEvent]) -> Intent:
        modalities = [e.modal for e in events]
        signals: dict = {}
        for e in events:
            sig = e.payload.get("signals")
            if isinstance(sig, dict):
                for k, v in sig.items():
                    signals.setdefault(k, []).extend(v)

        detail = {}
        # 收集各模态的有效载荷
        for e in events:
            if e.modal == "vision":
                detail["vision"] = e.payload
            if e.modal == "audio":
                detail["audio"] = e.payload
            if e.modal == "text":
                detail["text"] = e.payload

        name = self._pick_name(signals, modalities)
        confidence = self._confidence(name, signals)
        return Intent(name=name, confidence=confidence,
                      modalities=modalities, signals=signals, detail=detail)

    # ---- 内部 ----
    @staticmethod
    def _pick_name(signals: dict, modalities: List[str]) -> str:
        # 同时出现视觉+语音（或视觉/语音+文本查询）→ 多模态
        has_vis = any(k == "vision_query" for k in signals) or "vision" in modalities
        has_aud = any(k == "audio_query" for k in signals) or "audio" in modalities
        if has_vis and has_aud:
            return "multimodal"
        for name in ["quit", "help", "greeting", "vision_query", "audio_query", "status"]:
            if name in signals and signals[name]:
                return name
        return "unknown"

    @staticmethod
    def _confidence(name: str, signals: dict) -> float:
        if name in signals and signals[name]:
            return min(0.95, 0.5 + 0.15 * len(signals[name]))
        if name in ("vision_query", "audio_query", "multimodal"):
            return 0.6
        return 0.4
