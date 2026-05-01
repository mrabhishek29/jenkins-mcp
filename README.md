# Jenkins MCP

Custom MCP server for Jenkins, built on FastMCP + python-jenkins.
Credentials are stored in `config.yaml` — no `.env` files, no `load_dotenv` issues.

## One-Time Setup

Run this once inside `D:\jenkins-mcp`:

```
setup.cmd
```

This will:
1. Create a Python virtual environment (`.venv`)
2. Install all dependencies (`fastmcp`, `python-jenkins`, `pydantic`, etc.)
3. Copy `config.example.yaml` → `config.yaml` if it doesn't exist

Then edit **`config.yaml`** with your Jenkins credentials:

```yaml
jenkins:
  enabled: true
  base_url: https://jenkins.dev.e2open.com/jenkins
  username: your_username
  password: your_password
```

> **Note:** `config.yaml` is gitignored — your credentials are never committed.

## Use From Any VS Code Workspace

The whole point of this server is that you configure it **once** here, then reference it from **any** project.

### Step-by-step

1. Open your target project in VS Code
2. Create the file **`.vscode/mcp.json`** in that project (if it doesn't exist)
3. Add the server entry (see below)
4. Verify: `Ctrl+Shift+P` → **MCP: List Servers** — you should see `jenkins-mcp`

### Option A: Stdio (recommended)

**In this project's own workspace**, `.vscode/mcp.json` uses `${workspaceFolder}`:

```json
{
  "servers": {
    "jenkins-mcp": {
      "type": "stdio",
      "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
      "args": ["${workspaceFolder}\\server.py"]
    }
  }
}
```

**From any other project**, use the full absolute path:

```json
{
  "servers": {
    "jenkins-mcp": {
      "type": "stdio",
      "command": "D:\\jenkins-mcp\\.venv\\Scripts\\python.exe",
      "args": ["D:\\jenkins-mcp\\server.py"]
    }
  }
}
```

## Available Tools

### Job Discovery
| Tool | Description |
|---|---|
| `list_jobs` | List all Jenkins jobs, optionally filtered by view name |
| `search_jobs` | Search for jobs by name (case-insensitive) |
| `get_job_info` | Get full details of a job including last build status |

### Build Info & Logs
| Tool | Description |
|---|---|
| `get_build_info` | Get details and result of a specific build number |
| `get_last_build_status` | Get the result of the most recent build for a job |
| `get_build_console` | Get the full console log output of a specific build |
| `get_build_test_report` | Get JUnit test results for a specific build |

### Build Control
| Tool | Description |
|---|---|
| `trigger_build` | Trigger a build, with optional parameters for parameterised jobs |
| `stop_build` | Stop (abort) a running build |

### Queue Management
| Tool | Description |
|---|---|
| `get_queue` | List all items currently waiting in the build queue |
| `cancel_queue_item` | Cancel a queued build by its queue item ID |

### Nodes / Agents
| Tool | Description |
|---|---|
| `list_nodes` | List all Jenkins nodes/agents and their online/idle status |
| `get_node_info` | Get detailed info about a specific node |

### Views & Server
| Tool | Description |
|---|---|
| `list_views` | List all Jenkins views |
| `get_server_info` | Get Jenkins server version and basic server info |

## Running Tests

```
.venv\Scripts\pytest tests\
```
