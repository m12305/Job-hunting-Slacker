"""求职摆烂管理局桌面发行版的本地后端入口。"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="求职摆烂管理局本地服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    return parser.parse_args()


def configure_logging() -> None:
    log_file = os.environ.get("QIUZHAO_LOG_FILE")
    if not log_file:
        return
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
        force=True,
    )


def main() -> None:
    args = parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("桌面版后端只能监听本机地址")

    configure_logging()

    import uvicorn

    from app.main import app

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=args.port,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
