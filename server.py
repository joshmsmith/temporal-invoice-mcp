import os
import uuid
from typing import Dict

from fastmcp import MCPServer, tool
from temporalio.client import Client


async def _client() -> Client:
    return await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))


@tool
async def trigger(invoice: Dict) -> str:
    """Start the InvoiceWorkflow with the given invoice JSON."""
    client = await _client()
    handle = await client.start_workflow(
        "workflows.InvoiceWorkflow.run",
        invoice,
        id=f"invoice-{uuid.uuid4()}",
        task_queue="invoice-task-queue",
    )
    return handle.run_id


@tool
async def approve(run_id: str) -> str:
    """Signal approval for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    await handle.signal("ApproveInvoice")
    return "APPROVED"


@tool
async def reject(run_id: str) -> str:
    """Signal rejection for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    await handle.signal("RejectInvoice")
    return "REJECTED"


@tool
async def status(run_id: str) -> str:
    """Return current status of the workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    desc = await handle.describe()
    return desc.status.name


server = MCPServer(
    title="Invoice Tools",
    description="Manage invoice workflows via MCP",
    tools=[trigger, approve, reject, status],
)

if __name__ == "__main__":
    server.run()
