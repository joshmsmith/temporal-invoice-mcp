import os
import random
from temporalio import activity
from temporalio.exceptions import ApplicationError

FAIL_VALIDATE = os.getenv("FAIL_VALIDATE", "false").lower() == "true"
FAIL_PAYMENT = os.getenv("FAIL_PAYMENT", "false").lower() == "true"
NO_FAIL_PAYMENT = os.getenv("NO_FAIL_PAYMENT", "false").lower() == "true"

@activity.defn
async def validate_against_erp(invoice: dict) -> bool:
    activity.logger.info("Validating invoice %s", invoice.get("invoice_id"))
    if FAIL_VALIDATE or random.random() < 0.3:
        raise ApplicationError("MISMATCH")
    return True

@activity.defn
async def payment_gateway(line: dict) -> bool:
    activity.logger.info("Paying %s", line.get("description"))
    if FAIL_PAYMENT:
        raise ApplicationError(
            "INSUFFICIENT_FUNDS",
            type="INSUFFICIENT_FUNDS",
            non_retryable=True,
        )
    if not NO_FAIL_PAYMENT and random.random() < 0.3:
        raise ApplicationError(
            "INSUFFICIENT_FUNDS",
            type="INSUFFICIENT_FUNDS",
            non_retryable=True,
        )
    activity.logger.info("Payment succeeded")
    return True
