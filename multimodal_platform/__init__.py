"""多模态轻量化智能感知交互平台 (Multimodal Lightweight Intelligent Perception Platform).

一个面向边缘/低资源场景、可扩展的多模态感知与交互框架：
  感知(Perception) → 理解(Engine) → 交互(Interaction) 的轻量闭环。

设计原则：
- 轻量化：默认零第三方硬依赖，纯标准库即可运行；
- 可扩展：每个模块均为可替换的插件式接口，可平滑接入 ONNX/TFLite 等轻量模型；
- 多模态：视觉、语音、文本三类输入统一收敛到统一的感知事件，供引擎理解。
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
