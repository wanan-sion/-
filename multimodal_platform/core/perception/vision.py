"""视觉感知模块。

默认实现：
- `analyze_image`: 读取图片（若安装了 Pillow），输出宽高、平均亮度、主色调、
  色彩丰富度等轻量视觉特征；未安装 Pillow 时回退到仅返回文件元信息。
- 通过 `set_model` 可注入一个轻量模型推理回调（例如 ONNX MobileNet / TFLite），
  对图像做目标检测/分类，实现真正意义上的“智能感知”。

输出统一封装为 `PerceptionEvent(modal="vision", ...)`。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

try:  # 可选增强依赖
    from PIL import Image
    _HAS_PIL = True
except Exception:  # pragma: no cover
    _HAS_PIL = False


@dataclass
class PerceptionEvent:
    """统一的感知事件结构，供引擎理解。"""

    modal: str                # 模态: vision / audio / text
    source: str               # 来源描述
    payload: dict = field(default_factory=dict)   # 结构化感知结果
    raw: Any = None           # 原始输入（便于调试/扩展）
    confidence: float = 0.0   # 置信度 0~1


class VisionPerceiver:
    """轻量视觉感知器。"""

    def __init__(self, model: Optional[Callable[[str], dict]] = None):
        self._model = model

    def set_model(self, model: Callable[[str], dict]) -> None:
        """注入轻量模型推理回调：输入图像路径，返回 dict 形式的检测结果。"""
        self._model = model

    def analyze_image(self, image_path: str, source: str = "本地图片") -> PerceptionEvent:
        """分析一张图片，返回感知事件。"""
        payload: dict = {"path": image_path}

        if _HAS_PIL:
            try:
                img = Image.open(image_path)
                img.verify() if False else None
                img = Image.open(image_path).convert("RGB")
                w, h = img.size
                # 计算平均亮度与主色调（对缩小后的缩略图采样，保证轻量）
                thumb = img.resize((32, 32))
                pixels = list(thumb.getdata())
                n = len(pixels)
                avg = tuple(sum(p[i] for p in pixels) // n for i in range(3))
                brightness = round(0.299 * avg[0] + 0.587 * avg[1] + 0.114 * avg[2], 1)
                # 色彩丰富度：各通道标准差
                stds = []
                for ch in range(3):
                    mean = sum(p[ch] for p in pixels) / n
                    var = sum((p[ch] - mean) ** 2 for p in pixels) / n
                    stds.append(round(var ** 0.5, 1))
                colorfulness = round(sum(stds) / 3, 1)
                payload.update(
                    size=f"{w}x{h}",
                    avg_rgb=avg,
                    brightness=brightness,
                    colorfulness=colorfulness,
                )
            except Exception as e:  # pragma: no cover
                payload["error"] = f"图像解析失败: {e}"
        else:
            import os
            size = os.path.getsize(image_path)
            payload["hint"] = f"未安装 Pillow，仅返回文件信息（{size} 字节）"

        # 若注入了轻量模型，附加智能识别结果
        if self._model is not None:
            try:
                det = self._model(image_path) or {}
                payload["model_result"] = det
                payload["confidence"] = float(det.get("confidence", 0.0))
            except Exception as e:  # pragma: no cover
                payload["model_error"] = str(e)

        return PerceptionEvent(modal="vision", source=source, payload=payload,
                               confidence=payload.get("confidence", 0.0))


# 模块级便捷函数
def describe_scene(event: PerceptionEvent) -> str:
    """把视觉感知事件转成一句自然语言描述（演示用）。"""
    p = event.payload
    if "error" in p or "hint" in p and not p.get("brightness"):
        return f"未能充分解析图像（{p.get('error') or p.get('hint')}）"
    brightness = p.get("brightness", 0)
    light = "较亮" if brightness >= 128 else ("较暗" if brightness < 64 else "亮度适中")
    richness = "色彩丰富" if p.get("colorfulness", 0) >= 40 else "色彩素雅"
    model = p.get("model_result")
    if model:
        return (f"检测到 {model.get('label', '目标')}（置信度 {p.get('confidence', 0):.2f}），"
                f"画面{light}、{richness}，尺寸 {p.get('size')}。")
    return f"画面{light}、{richness}，平均亮度 {p.get('brightness')}，尺寸 {p.get('size')}。"
