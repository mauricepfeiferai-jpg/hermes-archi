"""Stripe webhook bridge for Harvey — HMAC verify + event handling."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time

log = logging.getLogger("harvey.stripe")

WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
TOLERANCE_SEC = 300  # Stripe default


class StripeBridge:
    def verify_and_parse(self, body: bytes, signature_header: str) -> dict:
        if not WEBHOOK_SECRET:
            log.warning("STRIPE_WEBHOOK_SECRET not set — skipping HMAC verify (dev only!)")
            try:
                return json.loads(body)
            except Exception as e:
                raise ValueError(f"invalid json: {e}") from e

        # Stripe sig header: t=...,v1=...,v0=...
        parts = {p.split("=")[0]: p.split("=")[1] for p in signature_header.split(",")
                 if "=" in p}
        ts = parts.get("t")
        v1 = parts.get("v1")
        if not ts or not v1:
            raise ValueError("missing t= or v1= in signature header")
        try:
            ts_int = int(ts)
        except ValueError:
            raise ValueError("non-integer timestamp")
        if abs(time.time() - ts_int) > TOLERANCE_SEC:
            raise ValueError("timestamp outside tolerance")

        signed = f"{ts}.{body.decode('utf-8')}"
        mac = hmac.new(WEBHOOK_SECRET.encode("utf-8"), signed.encode("utf-8"),
                       hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, v1):
            raise ValueError("hmac mismatch")
        return json.loads(body)

    async def handle_event(self, event: dict) -> dict:
        etype = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        if etype == "checkout.session.completed":
            return self._on_checkout_completed(data)
        if etype == "customer.subscription.created":
            return self._on_subscription_created(data)
        if etype == "customer.subscription.deleted":
            return self._on_subscription_deleted(data)
        if etype == "invoice.payment_failed":
            return self._on_payment_failed(data)
        if etype == "charge.refunded":
            return self._on_refund(data)

        return {"status": "ignored", "type": etype}

    def _on_checkout_completed(self, data: dict) -> dict:
        log.info("Checkout completed: %s", data.get("id"))
        return {"status": "processed", "action": "mark_user_paid",
                "customer": data.get("customer"), "amount": data.get("amount_total")}

    def _on_subscription_created(self, data: dict) -> dict:
        log.info("Subscription created: %s", data.get("id"))
        return {"status": "processed", "action": "activate_monthly_plan"}

    def _on_subscription_deleted(self, data: dict) -> dict:
        log.info("Subscription deleted: %s", data.get("id"))
        return {"status": "processed", "action": "deactivate_plan"}

    def _on_payment_failed(self, data: dict) -> dict:
        log.warning("Payment failed: %s", data.get("id"))
        return {"status": "processed", "action": "soft_lock_user_alert_maurice"}

    def _on_refund(self, data: dict) -> dict:
        log.warning("Refund: %s", data.get("id"))
        return {"status": "processed", "action": "lock_user_audit_note"}
