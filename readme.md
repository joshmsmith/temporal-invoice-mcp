# Invoice Demo with Temporal + MCP

### Prerequisites:

- Python3+
- `uv` (curl -LsSf https://astral.sh/uv/install.sh | sh)
- Temporal [Local Setup Guide](https://learn.temporal.io/getting_started/?_gl=1*1bxho70*_gcl_au*MjE1OTM5MzU5LjE3NDUyNjc4Nzk.*_ga*MjY3ODg1NzM5LjE2ODc0NTcxOTA.*_ga_R90Q9SJD3D*czE3NDc0MDg0NTIkbzk0NyRnMCR0MTc0NzQwODQ1MiRqMCRsMCRoMA..)
- [Claude for Desktop](https://claude.ai/download)

## 1. Clone & install

```
 git clone https://github.com/your-org/temporal-mcp-invoice-demo.git
 cd temporal-mcp-invoice-demo
 uv venv
 source .venv/bin/activate
 uv pip install temporalio fastmcp
```

## 2. Launch Temporal locally

```
 temporal server start-dev
```

## 3. Start the worker

```
 export TEMPORAL_ADDRESS=localhost:7233
 python worker.py [--fail-validate] [--fail-payment]
```

# Claude for Desktop Instructions (Sonnet 4)

## 1. Follow steps 1-3 above

## 2. Edit your Claude Config (Claude > Settings > Developer > Edit Config)

```json
{
  "mcpServers": {
    "invoice_processor": {
      "command": "/Path/To/Your/Install/Of/uv",
      "args": [
        "--directory",
        "/Path/To/temporal-invoice-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 3. Restart Claude for Desktop after editing your config

- If successful you'll see `invoice_processor` under 'Search & Tools'

## 4. To kick off processing the mock invoice, run:

```
trigger samples/invoice_acme.json
```

Use your MCP client (e.g., Claude Desktop) to call the `trigger`, `approve`,
`reject`, and `status` tools. The `trigger` tool now returns both the
`workflow_id` and `run_id` of the started workflow. Pass these values to the
`approve`, `reject`, and `status` tools. The sample invoice lives at
`samples/invoice_acme.json`. Inspect Temporal Web at `http://localhost:8233`.
Kill and restart the worker at any time to observe deterministic replay.
