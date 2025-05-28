# Invoice Demo with Temporal + MCP

## 1. Clone & install
```
 git clone https://github.com/your-org/temporal-mcp-invoice-demo.git
 cd temporal-mcp-invoice-demo
 pip install temporalio fastmcp mcp_tool click
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

## 4. Start the MCP server
```
 python server.py
```

Use your MCP client (e.g., Claude Desktop) to call the `trigger`, `approve`,
`reject`, and `status` tools. The sample invoice lives at
`samples/invoice_acme.json`. Inspect Temporal Web at
`http://localhost:8233`. Kill and restart the worker at any time to observe
deterministic replay.
