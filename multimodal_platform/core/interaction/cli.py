"""交互式命令行入口 (CLI)。

运行方式：
    python -m multimodal_platform.core.interaction.cli
或
    python app.py

纯标准库即可运行，启动后即可进行多模态感知对话演示。
"""

from __future__ import annotations

from .dialogue import DialogueManager
from .output import OutputFormatter

BANNER = r"""
============================================================
  多模态轻量化智能感知交互平台  v0.1.0
  感知(Perception) → 理解(Engine) → 交互(Interaction)
------------------------------------------------------------
  指令示例:
    你好 / 状态 / 帮助 / 退出
    看到 <图片路径>       → 视觉感知
    听到 <音频.wav 路径>  → 语音感知
  输入 exit 或 quit 退出
============================================================
"""


def main() -> int:
    manager = DialogueManager()
    print(BANNER)
    while True:
        try:
            user_input = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见，已退出。")
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "退出", "再见"):
            print("助手 > 再见，已退出。")
            break
        result = manager.turn(user_input)
        print("助手 > " + result["reply"])
        print("-" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
