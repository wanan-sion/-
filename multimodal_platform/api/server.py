"""REST API 层。

基于 FastAPI（可选依赖）暴露统一交互接口，便于前端/移动端/边缘网关接入：
- POST /v1/chat : 单轮交互（文本 + 可选图片/音频路径）
- GET  /health : 健康检查

未安装 FastAPI 时，API 层不会被导入，不影响核心功能运行。
"""

from __future__ import annotations

from typing import Optional

from ..core.interaction import DialogueManager

# 延迟导入，避免硬依赖
def _fastapi():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        return FastAPI, BaseModel
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("请先安装 fastapi: pip install fastapi uvicorn") from e


def create_app(manager: Optional[DialogueManager] = None):
    """创建 FastAPI 应用。"""
    FastAPI, BaseModel = _fastapi()
    manager = manager or DialogueManager()

    app = FastAPI(
        title="多模态轻量化智能感知交互平台 API",
        version="0.1.0",
        description="感知(Perception) → 理解(Engine) → 交互(Interaction) 的轻量闭环 API。",
    )

    class ChatRequest(BaseModel):
        text: str
        vision_path: Optional[str] = None
        audio_path: Optional[str] = None

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "multimodal-platform"}

    @app.post("/v1/chat")
    def chat(req: ChatRequest):
        # 组装多模态输入：文本 + 可选的图片/音频指令
        user_input = req.text
        if req.vision_path:
            user_input = f"看到 {req.vision_path}"
        elif req.audio_path:
            user_input = f"听到 {req.audio_path}"
        return manager.turn(user_input)

    return app
