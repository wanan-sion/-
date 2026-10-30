"""交互层 (Interaction Layer)。

职责：管理多轮会话上下文，把感知 + 理解 + 推理串成一次完整交互，
并把结果格式化为用户可读的输出。核心入口 `DialogueManager.turn()`。
"""

from .dialogue import DialogueManager
from .output import OutputFormatter

__all__ = ["DialogueManager", "OutputFormatter"]
