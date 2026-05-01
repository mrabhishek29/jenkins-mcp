"""Jenkins tools for the Jenkins MCP server."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import jenkins
from fastmcp import FastMCP

from config import JenkinsConfig

logger = logging.getLogger(__name__)


def register_jenkins_tools(mcp: FastMCP, cfg: JenkinsConfig) -> None:
    """Register all Jenkins tools with the MCP server."""

    server = jenkins.Jenkins(
        cfg.base_url,
        username=cfg.username,
        password=cfg.password,
    )

    # -------------------------------------------------------------------------
    # Job discovery
    # -------------------------------------------------------------------------

    @mcp.tool()
    def list_jobs(view_name: str = "") -> List[Dict[str, Any]]:
        """List all Jenkins jobs. Optionally filter by view name."""
        if view_name:
            jobs = server.get_jobs(view_name=view_name)
        else:
            jobs = server.get_jobs()
        return [
            {
                "name": j["name"],
                "url": j["url"],
                "color": j.get("color"),
            }
            for j in jobs
        ]

    @mcp.tool()
    def search_jobs(query: str) -> List[Dict[str, Any]]:
        """Search for jobs whose full name contains the query string (case-insensitive)."""
        all_jobs = server.get_all_jobs()
        q = query.lower()
        return [
            {
                "name": j["fullname"],
                "url": j["url"],
                "color": j.get("color"),
            }
            for j in all_jobs
            if q in j["fullname"].lower()
        ]

    @mcp.tool()
    def get_job_info(job_name: str) -> Dict[str, Any]:
        """Get full details of a Jenkins job including last build status."""
        info = server.get_job_info(job_name)
        lb = info.get("lastBuild") or {}
        lsb = info.get("lastSuccessfulBuild") or {}
        lfb = info.get("lastFailedBuild") or {}
        return {
            "name": info["name"],
            "url": info["url"],
            "description": info.get("description"),
            "buildable": info.get("buildable"),
            "last_build_number": lb.get("number"),
            "last_build_url": lb.get("url"),
            "last_successful_build_number": lsb.get("number"),
            "last_failed_build_number": lfb.get("number"),
            "next_build_number": info.get("nextBuildNumber"),
            "in_queue": info.get("inQueue"),
        }

    # -------------------------------------------------------------------------
    # Build info & logs
    # -------------------------------------------------------------------------

    @mcp.tool()
    def get_build_info(job_name: str, build_number: int) -> Dict[str, Any]:
        """Get details and result of a specific build number."""
        info = server.get_build_info(job_name, build_number)
        return {
            "number": info["number"],
            "result": info.get("result"),
            "duration_ms": info.get("duration"),
            "estimated_duration_ms": info.get("estimatedDuration"),
            "timestamp": info.get("timestamp"),
            "url": info["url"],
            "building": info.get("building"),
            "display_name": info.get("displayName"),
        }

    @mcp.tool()
    def get_last_build_status(job_name: str) -> Dict[str, Any]:
        """Get the result of the most recent build for a job."""
        info = server.get_job_info(job_name)
        lb = info.get("lastBuild")
        if not lb:
            return {"job": job_name, "status": "No builds found"}
        build = server.get_build_info(job_name, lb["number"])
        return {
            "job": job_name,
            "build_number": build["number"],
            "result": build.get("result"),
            "building": build.get("building"),
            "duration_ms": build.get("duration"),
            "url": build["url"],
        }

    @mcp.tool()
    def get_build_console(job_name: str, build_number: int) -> str:
        """Get the full console log output of a specific build."""
        return server.get_build_console_output(job_name, build_number)

    @mcp.tool()
    def get_build_test_report(job_name: str, build_number: int) -> Dict[str, Any]:
        """Get test results for a specific build (requires JUnit plugin)."""
        try:
            report = server.get_build_test_report(job_name, build_number)
            if not report:
                return {"message": "No test report available for this build."}
            return {
                "total": report.get("totalCount"),
                "failed": report.get("failCount"),
                "skipped": report.get("skipCount"),
                "passed": report.get("passCount"),
                "duration": report.get("duration"),
            }
        except Exception as exc:
            return {"error": str(exc)}

    # -------------------------------------------------------------------------
    # Build triggering
    # -------------------------------------------------------------------------

    @mcp.tool()
    def trigger_build(job_name: str, parameters: Optional[Dict[str, str]] = None) -> str:
        """Trigger a Jenkins build. Pass a parameters dict for parameterised jobs."""
        if parameters:
            queue_id = server.build_job(job_name, parameters=parameters)
        else:
            queue_id = server.build_job(job_name)
        return f"Build queued successfully. Queue item ID: {queue_id}"

    @mcp.tool()
    def stop_build(job_name: str, build_number: int) -> str:
        """Stop (abort) a running build."""
        server.stop_build(job_name, build_number)
        return f"Stop signal sent to {job_name} #{build_number}."

    # -------------------------------------------------------------------------
    # Queue
    # -------------------------------------------------------------------------

    @mcp.tool()
    def get_queue() -> List[Dict[str, Any]]:
        """Get all items currently waiting in the Jenkins build queue."""
        queue = server.get_queue_info()
        return [
            {
                "id": item["id"],
                "job_name": item["task"]["name"],
                "why": item.get("why"),
                "stuck": item.get("stuck"),
                "blocked": item.get("blocked"),
            }
            for item in queue
        ]

    @mcp.tool()
    def cancel_queue_item(queue_item_id: int) -> str:
        """Cancel a queued build by its queue item ID."""
        server.cancel_queue_item(queue_item_id)
        return f"Queue item {queue_item_id} cancelled."

    # -------------------------------------------------------------------------
    # Nodes / Agents
    # -------------------------------------------------------------------------

    @mcp.tool()
    def list_nodes() -> List[Dict[str, Any]]:
        """List all Jenkins nodes (agents) and their online/idle status."""
        nodes = server.get_nodes()
        return [
            {
                "name": n["name"],
                "offline": n.get("offline"),
                "idle": n.get("idle"),
            }
            for n in nodes
        ]

    @mcp.tool()
    def get_node_info(node_name: str) -> Dict[str, Any]:
        """Get detailed info about a specific Jenkins node."""
        info = server.get_node_info(node_name)
        return {
            "name": info.get("displayName"),
            "offline": info.get("offline"),
            "temporarily_offline": info.get("temporarilyOffline"),
            "offline_cause": info.get("offlineCauseReason"),
            "idle": info.get("idle"),
            "num_executors": info.get("numExecutors"),
        }

    # -------------------------------------------------------------------------
    # Views
    # -------------------------------------------------------------------------

    @mcp.tool()
    def list_views() -> List[Dict[str, Any]]:
        """List all Jenkins views."""
        views = server.get_views()
        return [{"name": v["name"], "url": v["url"]} for v in views]

    # -------------------------------------------------------------------------
    # Server info
    # -------------------------------------------------------------------------

    @mcp.tool()
    def get_server_info() -> Dict[str, Any]:
        """Get Jenkins server version and basic info."""
        version = server.get_version()
        info = server.get_info()
        return {
            "version": version,
            "num_executors": info.get("numExecutors"),
            "mode": info.get("mode"),
            "node_name": info.get("nodeName"),
            "quieting_down": info.get("quietingDown"),
            "slave_agent_port": info.get("slaveAgentPort"),
        }

    logger.info("Jenkins tools registered successfully")
