"""Jenkins MCP server – built using fastmcp + python-jenkins.

Reads credentials from config.yaml and registers Jenkins tools.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Tuple

from fastmcp import FastMCP

from config import Config
from logging_setup import setup_logging

__version__ = "0.1.0"


def create_server(config_path: str | None = None) -> Tuple[FastMCP, Config]:
    """Create and configure the MCP server.

    Args:
        config_path: Path to config.yaml. Defaults to MCP_CONFIG_PATH env var
                     or config.yaml next to this file.

    Returns:
        Tuple of (FastMCP instance, loaded Config).
    """
    if config_path is None:
        config_path = os.getenv("MCP_CONFIG_PATH", str(Path(__file__).resolve().parent / "config.yaml"))

    cfg = Config.load(config_path)
    setup_logging(cfg.logging)

    mcp = FastMCP("jenkins-mcp")

    if cfg.jenkins and cfg.jenkins.enabled:
        from jenkins_tools import register_jenkins_tools
        register_jenkins_tools(mcp, cfg.jenkins)

    return mcp, cfg


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    mcp, cfg = create_server()

    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        transport = "streamable-http"

    if transport == "streamable-http":
        mcp.run(transport=transport, host=cfg.server.host, port=cfg.server.port)
    else:
        mcp.run(transport=transport)
