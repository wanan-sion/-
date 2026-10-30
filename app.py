"""多模态轻量化智能感知交互平台 — 主入口。

用法:
    python app.py                 # 启动命令行交互
    python app.py --server        # 启动 REST API 服务 (需 fastapi/uvicorn)

示例（一次感知调用）:
    python -c "from multimodal_platform.core.interaction import DialogueManager; \
    print(DialogueManager().turn('你好')['reply'])"
"""

from __future__ import annotations

import sys


def main(argv: list = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--server" in argv or "-s" in argv:
        return _run_server()
    return _run_cli()


def _run_cli() -> int:
    from multimodal_platform.core.interaction.cli import main as cli_main
    return cli_main()


def _run_server() -> int:
    try:
        import uvicorn
    except ImportError:
        print("启动 API 服务需要: pip install fastapi uvicorn")
        return 1
    from multimodal_platform.api.server import create_app
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
