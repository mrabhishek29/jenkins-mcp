"""Logging setup for the Jenkins MCP server."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    if config is None:
        config = LoggingConfig()

    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    detailed = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    simple = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")

    root = logging.getLogger()
    root.setLevel(config.level)
    root.handlers = []

    fh = RotatingFileHandler(log_dir / "jenkins-mcp.log", maxBytes=5_000_000, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(detailed)
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(config.level)
    ch.setFormatter(simple)
    root.addHandler(ch)

    # Silence noisy libraries
    for name in ("urllib3", "requests"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.info("Logging initialized")
