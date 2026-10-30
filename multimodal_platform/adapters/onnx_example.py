"""ONNX 轻量模型接入示例。

演示如何把任意 ONNX 分类/检测模型封装成感知模块可接受的
`Callable[[image_path], dict]` 回调。运行时需额外安装：
    pip install onnxruntime pillow numpy

该回调可直接注入 `VisionPerceiver.set_model()`，从而实现真正的轻量智能感知。
"""

from __future__ import annotations

from typing import Callable, List


def create_onnx_classifier(
    model_path: str,
    labels: List[str],
    input_size: int = 224,
) -> Callable[[str], dict]:
    """返回一个对图像做分类的推理回调。

    参数:
        model_path: ONNX 模型路径
        labels:     类别标签列表（顺序与模型输出一致）
        input_size: 输入尺寸（正方形）
    """
    import numpy as np
    from PIL import Image
    import onnxruntime as ort

    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    def classify(image_path: str) -> dict:
        img = Image.open(image_path).convert("RGB").resize((input_size, input_size))
        arr = np.asarray(img).astype("float32") / 255.0
        # CHW + batch，按模型要求归一化（示例用 0-1 归一化，实际以模型为准）
        data = np.expand_dims(arr.transpose(2, 0, 1), 0)
        logits = session.run(None, {input_name: data})[0][0]
        idx = int(np.argmax(logits))
        return {
            "label": labels[idx] if idx < len(labels) else f"class_{idx}",
            "confidence": float(1.0 / (1.0 + np.exp(-float(logits[idx])))),
        }

    return classify
