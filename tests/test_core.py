"""核心闭环单元测试（使用标准库 unittest，无需额外依赖）。

运行: python -m unittest discover -s tests
"""

import os
import sys
import unittest
import wave
import struct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multimodal_platform.core.perception import TextPerceiver, VisionPerceiver, AudioPerceiver
from multimodal_platform.core.engine import IntentRecognizer, RuleReasoner
from multimodal_platform.core.interaction import DialogueManager


class TestTextPerception(unittest.TestCase):
    def setUp(self):
        self.tp = TextPerceiver()

    def test_normalize(self):
        self.assertEqual(self.tp.normalize("  你好 世界 "), "你好 世界")

    def test_greeting_signal(self):
        ev = self.tp.analyze("你好呀")
        self.assertIn("greeting", ev.payload["signals"])

    def test_vision_signal(self):
        ev = self.tp.analyze("看到一张图片")
        self.assertIn("vision_query", ev.payload["signals"])


class TestVisionPerception(unittest.TestCase):
    def test_no_pil_fallback(self):
        # 未装 Pillow 也不报错，返回文件信息
        vp = VisionPerceiver()
        ev = vp.analyze_image("/nonexistent/x.jpg")
        self.assertEqual(ev.modal, "vision")
        self.assertIn("path", ev.payload)


class TestAudioPerception(unittest.TestCase):
    @staticmethod
    def _make_wav(path, duration=0.3, freq=440, amplitude=2000):
        framerate = 8000
        n = int(duration * framerate)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(framerate)
            frames = b"".join(
                struct.pack("<h", int(amplitude * 0.5 * (1 + 0.0)) if False else
                            int(amplitude * (0.5 + 0.5))) for _ in range(n))
            wf.writeframes(frames)

    def test_analyze_wav(self):
        path = "/tmp/_test_tone.wav"
        self._make_wav(path)
        ap = AudioPerceiver()
        ev = ap.analyze_wav(path)
        os.remove(path)
        self.assertEqual(ev.modal, "audio")
        self.assertIn("duration", ev.payload)
        self.assertGreater(ev.payload["duration"], 0)


class TestIntentRecognizer(unittest.TestCase):
    def test_greeting(self):
        r = IntentRecognizer()
        ev = TextPerceiver().analyze("你好")
        intent = r.recognize([ev])
        self.assertEqual(intent.name, "greeting")

    def test_quit(self):
        r = IntentRecognizer()
        ev = TextPerceiver().analyze("退出")
        intent = r.recognize([ev])
        self.assertEqual(intent.name, "quit")


class TestDialogue(unittest.TestCase):
    def test_round_trip(self):
        dm = DialogueManager()
        res = dm.turn("你好")
        self.assertEqual(res["intent"], "greeting")
        self.assertIn("reply", res)

    def test_help(self):
        dm = DialogueManager()
        res = dm.turn("帮助")
        self.assertEqual(res["intent"], "help")

    def test_status(self):
        dm = DialogueManager()
        res = dm.turn("汇报状态")
        self.assertEqual(res["intent"], "status")


if __name__ == "__main__":
    unittest.main()
