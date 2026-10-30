"""极简配置加载。

优先读取 YAML（若安装了 PyYAML），否则读取 JSON，最后回退到内置默认值。
保持零硬依赖，让项目在任何环境都能启动。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "app": {
        "name": "多模态轻量感知交互平台",
        "version": "0.1.0",
        "history_size": 10,
    },
    "perception": {
        "vision": {"enabled": True},
        "audio": {"enabled": True},
        "text": {"enabled": True},
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
    },
}


def load_config(path: str | None = None) -> Dict[str, Any]:
    """加载配置：YAML/JSON 文件或默认值。"""
    cfg = json.loads(json.dumps(DEFAULTS))  # 深拷贝
    if not path:
        return cfg
    p = Path(path)
    if not p.exists():
        return cfg
    try:
        import yaml  # 可选依赖
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except ImportError:
        if p.suffix in (".json",):
            data = json.loads(p.read_text(encoding="utf-8"))
        else:  # 尝试按 JSON 兜底
            data = json.loads(p.read_text(encoding="utf-8"))
    _merge(cfg, data)
    return cfg


def _merge(base: dict, override: dict) -> None:
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v
