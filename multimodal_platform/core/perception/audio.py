"""语音/音频感知模块。

默认实现（纯标准库）：
- `analyze_wav`: 解析 WAV 文件，输出时长、平均响度、静音占比、是否存在有效语音片段
  （基于能量阈值的语音活动检测 VAD，轻量级启发式）。
- 通过 `set_asr` 可注入 ASR（语音转文字）回调，得到真正的语音内容感知。

输出统一封装为 `PerceptionEvent(modal="audio", ...)`。
"""

from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from typing import Any, Callable, Optional

try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:  # pragma: no cover
    _HAS_NUMPY = False

from .vision import PerceptionEvent


class AudioPerceiver:
    """轻量音频感知器。"""

    def __init__(self, asr: Optional[Callable[[str], str]] = None):
        self._asr = asr

    def set_asr(self, asr: Callable[[str], str]) -> None:
        """注入 ASR 回调：输入音频路径，返回转写文本。"""
        self._asr = asr

    def analyze_wav(self, wav_path: str, source: str = "本地音频") -> PerceptionEvent:
        """分析一个 WAV 文件，返回感知事件。"""
        payload: dict = {"path": wav_path}
        try:
            with wave.open(wav_path, "rb") as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                duration = n_frames / framerate
                payload.update(
                    channels=n_channels,
                    sample_width=sampwidth,
                    sample_rate=framerate,
                    duration=round(duration, 2),
                )
                if sampwidth != 2 or n_channels > 2:  # 非 16bit PCM 不做能量分析
                    payload["hint"] = "非 16bit PCM，跳过能量分析"
                else:
                    frames = wf.readframes(n_frames)
                    samples = self._to_samples(frames, n_channels)
                    self._energy_stats(samples, framerate, payload)
        except Exception as e:  # pragma: no cover
            payload["error"] = f"音频解析失败: {e}"

        if self._asr is not None:
            try:
                payload["transcript"] = self._asr(wav_path)
            except Exception as e:  # pragma: no cover
                payload["asr_error"] = str(e)

        return PerceptionEvent(modal="audio", source=source, payload=payload,
                               confidence=payload.get("voice_ratio", 0.0))

    # ---- 内部工具 ----
    @staticmethod
    def _to_samples(frames: bytes, channels: int) -> list:
        if _HAS_NUMPY:
            arr = np.frombuffer(frames, dtype=np.int16)
            return arr.reshape(-1, channels)[:, 0].tolist() if channels == 2 else arr.tolist()
        n = len(frames) // 2
        return [struct.unpack("<h", frames[i * 2:i * 2 + 2])[0] for i in range(n)]

    @staticmethod
    def _energy_stats(samples: list, framerate: int, payload: dict) -> None:
        if not samples:
            payload["hint"] = "无有效采样"
            return
        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
        # 分帧计算每帧能量，统计“有声音”占比（轻量 VAD）
        frame_len = max(1, framerate // 10)  # 100ms 一帧
        voiced = 0
        frames = 0
        for i in range(0, len(samples), frame_len):
            chunk = samples[i:i + frame_len]
            if not chunk:
                continue
            frames += 1
            e = math.sqrt(sum(s * s for s in chunk) / len(chunk))
            if e > 500:  # 经验阈值，视为语音活动
                voiced += 1
        payload["rms_energy"] = round(rms, 1)
        payload["voice_ratio"] = round(voiced / frames, 2) if frames else 0.0
        payload["voice_active"] = voiced / frames > 0.05 if frames else False


def describe_audio(event: PerceptionEvent) -> str:
    """把音频感知事件转成一句自然语言描述（演示用）。"""
    p = event.payload
    if p.get("error"):
        return f"音频解析失败（{p['error']}）"
    transcript = p.get("transcript")
    if transcript:
        return f"识别到语音内容：{transcript}"
    active = p.get("voice_active")
    ratio = p.get("voice_ratio", 0.0)
    state = "包含语音片段" if active else "主要为静音/噪声"
    return (f"{state}（语音占比 {ratio:.0%}），时长 {p.get('duration')}s，"
            f"能量 {p.get('rms_energy')}。")
