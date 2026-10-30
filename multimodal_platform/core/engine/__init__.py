"""理解/引擎层 (Engine Layer)。

职责：把感知层输出的多模态感知事件，统一收敛为意图(Intent)与结构化上下文，
再由轻量推理器(Reasoner)生成回复。分层：
- intent   ：意图识别与多模态融合
- reasoning：轻量回答/决策生成
"""

from .intent import IntentRecognizer
from .reasoning import RuleReasoner

__all__ = ["IntentRecognizer", "RuleReasoner"]
