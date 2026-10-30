"""核心层：感知 + 理解 + 交互 三大子系统的聚合入口。"""

from . import perception, engine, interaction

__all__ = ["perception", "engine", "interaction"]
