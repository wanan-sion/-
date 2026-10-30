"""轻量推理器。

根据识别出的意图(Intent)与多模态感知详情，生成自然语言回复。
默认实现为“规则 + 感知数据回填”的轻量方案，零依赖、可离线运行，
非常适合边缘/嵌入式场景；也可替换为调用云端/本地轻量 LLM 的更强推理器。
"""

from __future__ import annotations

from .intent import Intent, INTENT_LABELS
from ..perception.vision import describe_scene
from ..perception.audio import describe_audio


class RuleReasoner:
    """规则推理器：把意图与感知数据组织成可读回复。"""

    def reply(self, intent: Intent) -> str:
        name = intent.name
        detail = intent.detail

        if name == "greeting":
            return ("你好！我是多模态轻量感知助手。你可以对我说“看看这张图”“听听这段音频”"
                    "或“汇报状态”，我会基于视觉/语音/文本感知回答。输入“帮助”了解更多。")

        if name == "status":
            return self._status_reply(detail)

        if name == "vision_query":
            return self._vision_reply(detail)

        if name == "audio_query":
            return self._audio_reply(detail)

        if name == "multimodal":
            return self._multimodal_reply(detail)

        if name == "help":
            return ("支持的指令：\n"
                    "  1) 文本对话：直接输入任意内容\n"
                    "  2) 视觉感知：输入 `看到 <图片路径>` 或 `识别 <图片路径>`\n"
                    "  3) 语音感知：输入 `听到 <音频路径>` 或 `听 <wav路径>`\n"
                    "  4) 状态汇报：输入 `状态` 或 `汇报`\n"
                    "  5) 退出：输入 `退出` 或 `quit`")

        if name == "quit":
            return "再见，已退出。"

        return self._fallback_reply(detail)

    # ---- 各意图的回复组装 ----
    @staticmethod
    def _status_reply(detail: dict) -> str:
        vis = detail.get("vision") or {}
        aud = detail.get("audio") or {}
        parts = []
        if vis:
            parts.append("视觉模块正常")
        if aud:
            parts.append("语音模块正常")
        if not parts:
            parts.append("文本模块正常，所有感知模块待命")
        return "系统状态：运行正常。感知模块：" + "、".join(parts) + "。"

    @staticmethod
    def _vision_reply(detail: dict) -> str:
        vis = detail.get("vision")
        if not vis or "path" not in vis:
            return "请提供要分析的图片路径，例如：看到 /path/to/image.jpg"
        from ..perception.vision import VisionPerceiver
        ev = PerceptionEventStub(vis)
        return "视觉感知结果：" + describe_scene(ev)

    @staticmethod
    def _audio_reply(detail: dict) -> str:
        aud = detail.get("audio")
        if not aud or "path" not in aud:
            return "请提供要分析的音频路径，例如：听到 /path/to/audio.wav"
        ev = PerceptionEventStub(aud)
        return "语音感知结果：" + describe_audio(ev)

    @staticmethod
    def _multimodal_reply(detail: dict) -> str:
        vis = detail.get("vision")
        aud = detail.get("audio")
        parts = []
        if vis:
            parts.append("视觉：" + describe_scene(PerceptionEventStub(vis)))
        if aud:
            parts.append("语音：" + describe_audio(PerceptionEventStub(aud)))
        if not parts:
            return "已融合多模态感知，但缺少有效感知数据。"
        return "多模态融合感知结果——\n" + "\n".join(parts)

    @staticmethod
    def _fallback_reply(detail: dict) -> str:
        txt = (detail.get("text") or {}).get("text", "")
        if txt:
            return f"我听到了你的话：{txt}。当前为轻量规则模式，如需语义理解可接入模型。"
        return "抱歉，我暂时无法理解这个输入。输入“帮助”查看支持的指令。"


class PerceptionEventStub:
    """把 intent.detail 中的 payload 包装为 PerceptionEvent，便于复用描述函数。"""

    def __init__(self, payload: dict):
        self.payload = payload


__all__ = ["RuleReasoner", "INTENT_LABELS"]
