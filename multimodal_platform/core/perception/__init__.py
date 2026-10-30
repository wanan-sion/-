"""感知层 (Perception Layer)。

职责：把来自不同传感器/数据源的原始信号，转换为结构化的“感知事件”(PerceptionEvent)，
供上层引擎统一理解。三类模态：
- vision：视觉感知（图像特征、场景描述、目标检测接口）
- audio ：语音感知（响度、静音、语音活动检测接口）
- text  ：文本感知（输入归一化、关键词抽取）

默认实现使用纯标准库；若要更高精度，可通过 Adapter 接入轻量推理模型。
"""

from .vision import VisionPerceiver
from .audio import AudioPerceiver
from .text import TextPerceiver

__all__ = ["VisionPerceiver", "AudioPerceiver", "TextPerceiver"]
