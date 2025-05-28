from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List

from temporalio import workflow
from temporalio.common import RetryPolicy

from activities import validate_against_erp, payment_gateway


def _parse_due_date(due: str) -> datetime:
    if due.endswith("Z"):
        due = due[:-1] + "+00:00"
    return datetime.fromisoformat(due)


@workflow.defn
class PayLineItem:
    @workflow.run
    async def run(self, line: dict) -> None:
        due = _parse_due_date(line["due_date"])
        delay = (due - workflow.now()).total_seconds()
        if delay > 0:
            await workflow.sleep(delay)
        await workflow.execute_activity(
            payment_gateway,
            line,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
                non_retryable_error_types=["INSUFFICIENT_FUNDS"],
            ),
        )


@workflow.defn
class InvoiceWorkflow:
    def __init__(self) -> None:
        self.approved: bool | None = None

    @workflow.signal
    async def ApproveInvoice(self) -> None:
        self.approved = True

    @workflow.signal
    async def RejectInvoice(self) -> None:
        self.approved = False

    @workflow.run
    async def run(self, invoice: dict) -> str:
        await workflow.execute_activity(
            validate_against_erp,
            invoice,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
        )

        await workflow.wait_condition(
            lambda: self.approved is not None,
            timeout=timedelta(days=5),
        )

        if not self.approved:
            workflow.logger.info("REJECTED")
            return "REJECTED"

        results = []
        for line in invoice.get("lines", []):
            handle = await workflow.start_child_workflow(PayLineItem.run, line)
            results.append(handle)
        for h in results:
            await h.result()
        workflow.logger.info("PAID")
        return "PAID"
