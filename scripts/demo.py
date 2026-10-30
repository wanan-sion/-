"""一键演示脚本：展示多模态感知交互闭环。

运行:
    python scripts/demo.py

输出一次包含 文本 → 意图 → 回复、视觉感知、音频感知 的完整演示。
"""

import os
import sys
import wave
import struct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multimodal_platform.core.interaction import DialogueManager


def _make_demo_audio(path: str) -> None:
    """生成一段演示用的正弦波 WAV。"""
    framerate = 8000
    duration = 0.4
    n = int(duration * framerate)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        frames = b"".join(struct.pack("<h", 3000) for _ in range(n))
        wf.writeframes(frames)


def main() -> int:
    dm = DialogueManager()
    print("=" * 60)
    print("多模态轻量化智能感知交互平台 — 演示")
    print("=" * 60)

    for text in ("你好", "汇报状态", "帮助"):
        res = dm.turn(text)
        print(f"[{res['intent_label']}] {text}")
        print(f"   -> {res['reply']}\n")

    # 音频感知演示
    audio_path = "/tmp/demo_audio.wav"
    _make_demo_audio(audio_path)
    res = dm.turn(f"听到 {audio_path}")
    print(f"[{res['intent_label']}] 听到演示音频")
    print(f"   -> {res['reply']}")
    os.remove(audio_path)

    print("=" * 60)
    print("演示完成 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
