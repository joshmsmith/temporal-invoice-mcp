# 1. Clone & install

git clone https://github.com/your-org/temporal-mcp-invoice-demo.git
cd temporal-mcp-invoice-demo
pip install -r requirements.txt # temporalio, mcp_tool, click

# 2. Launch Temporal locally

temporal server start-dev # Temporal Server + Web

# 3. Start the worker

export TEMPORAL_ADDRESS=localhost:7233
python worker.py

# 4. Kick off a run

python cli.py trigger samples/invoice_acme.json

# copy the run-id from the output

# 5. Approve the invoice

python cli.py approve <RUN_ID>

# 6. Watch history

open http://localhost:8233
