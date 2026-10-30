"""模型适配层 (Adapters)。

“轻量化”的关键在于把重量级模型换成轻量推理，本层负责统一接入 ONNX / TFLite /
HuggingFace 等轻量模型的推理回调，让感知模块无需关心底层引擎细节。

本目录为预留接口位，附一个 ONNX 示例供参考。
"""

from .onnx_example import create_onnx_classifier

__all__ = ["create_onnx_classifier"]
