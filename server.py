import os
import uuid
from typing import Dict

from mcp.server.fastmcp import FastMCP, Context
from temporalio.client import Client

from workflows import InvoiceWorkflow


async def _client() -> Client:
    return await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))


mcp = FastMCP("invoice_processor")


@mcp.tool()
async def trigger(invoice: Dict, ctx: Context) -> Dict[str, str]:
    await ctx.report_progress(progress=0.1, total=1.0)
    await ctx.info("Starting invoice processing workflow")
    """Start the InvoiceWorkflow with the given invoice JSON."""
    workflow_id = f"invoice-{uuid.uuid4()}"
    client = await _client()
    handle = await client.start_workflow(
        InvoiceWorkflow.run,
        invoice,
        id=workflow_id,
        task_queue="invoice-task-queue",
    )
    await ctx.info("Invoice processing workflow started")
    
    desc = await handle.describe()
    status = await handle.query("GetInvoiceStatus")
    await ctx.report_progress(progress=1.0, total=1.0)
    await ctx.info(f"Invoice processing workflow started with status {status}")
    
    
    return {"workflow_id": handle.id, "run_id": handle.result_run_id}


@mcp.tool()
async def approve(workflow_id: str, run_id: str) -> str:
    """Signal approval for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    await handle.signal("ApproveInvoice")
    return "APPROVED"


@mcp.tool()
async def reject(workflow_id: str, run_id: str) -> str:
    """Signal rejection for the invoice workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    await handle.signal("RejectInvoice")
    return "REJECTED"


@mcp.tool()
async def status(workflow_id: str, run_id: str) -> str:
    """Return current status of the workflow."""
    client = await _client()
    handle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    desc = await handle.describe()
    status = await handle.query("GetInvoiceStatus")
    return f"Invoice with ID {workflow_id} is currently {status}. " \
           f"Workflow status: {desc.status.name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
