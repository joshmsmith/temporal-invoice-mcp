import os
import uuid
from typing import Dict

from mcp.server.fastmcp import FastMCP
from temporalio.client import Client


async def _client() -> Client:
    return await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))

mcp = FastMCP("invoice_processor")

@mcp.tool()
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


@mcp.tool()
async def approve(run_id: str) -> str:
    """Signal approval for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    await handle.signal("ApproveInvoice")
    return "APPROVED"


@mcp.tool()
async def reject(run_id: str) -> str:
    """Signal rejection for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    await handle.signal("RejectInvoice")
    return "REJECTED"


@mcp.tool()
async def status(run_id: str) -> str:
    """Return current status of the workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id="", run_id=run_id)
    desc = await handle.describe()
    return desc.status.name

if __name__ == "__main__":
    mcp.run(transport='stdio')
