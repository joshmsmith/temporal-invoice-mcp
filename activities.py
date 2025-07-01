import os
import random
from temporalio import activity
from temporalio.exceptions import ApplicationError
from temporalio.client import Client


@activity.defn
async def validate_against_erp(invoice: dict) -> bool:
    activity.logger.info("Validating invoice %s", invoice.get("invoice_id"))
    fail_validate = os.getenv("FAIL_VALIDATE", "false").lower() == "true"
    if fail_validate or random.random() < 0.3:
        raise ApplicationError("MISMATCH")
    return True

@activity.defn
async def payment_gateway(line: dict) -> bool:
    activity.logger.info("Paying %s", line.get("description"))
    fail_payment = os.getenv("FAIL_PAYMENT", "false").lower() == "true"
    no_fail_payment = os.getenv("NO_FAIL_PAYMENT", "false").lower() == "true"
    if fail_payment:
        raise ApplicationError(
            "INSUFFICIENT_FUNDS",
            type="INSUFFICIENT_FUNDS",
            non_retryable=True,
        )
    if not no_fail_payment and random.random() < 0.1:
        raise ApplicationError(
            "INSUFFICIENT_FUNDS",
            type="INSUFFICIENT_FUNDS",
            non_retryable=True,
        )
    # Simulate a retryable failure sometimes for payment processing
    if random.random() < 0.3:
        raise ApplicationError("PAYMENT_GATEWAY_ERROR", type="PAYMENT_GATEWAY_ERROR")
    activity.logger.info("Payment succeeded")
    return True

@activity.defn
async def callback(status: str) -> str:
    # Attempt to call back to the agent to notify them of the status
    activity.logger.info("Callback with status: %s", status)
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))
    try:
        signal_wf_id = "agent-workflow"
        signal_name = "add_external_message"
        handle = client.get_workflow_handle(workflow_id=signal_wf_id)
        await handle.signal(signal_name, f"Invoice processing complete with status: {status}" )
    except Exception as e:
        activity.logger.error("Callback failed: %s", e)
        raise ApplicationError(f"Callback failed: {e}")

    activity.logger.info("Callback succeeded")
    return "SUCCESS"
