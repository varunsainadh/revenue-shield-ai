from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.domain.enums import FraudAlertType, FraudSeverity, FraudAlertStatus
from app.domain.fraud import FraudAlertDomain

class FraudDetector:
    @staticmethod
    def inspect_refund_event(
        payment_id: str,
        customer_id: str,
        amount: float,
        recent_refunds_count: int = 0,
        is_duplicate: bool = False
    ) -> List[FraudAlertDomain]:
        alerts: List[FraudAlertDomain] = []

        # Rule 1: Duplicate Refund Detection
        if is_duplicate:
            alerts.append(FraudAlertDomain(
                transaction_id=payment_id,
                customer_id=customer_id,
                alert_type=FraudAlertType.DUPLICATE_REFUND,
                severity=FraudSeverity.HIGH,
                description=f"Duplicate refund request detected for Payment {payment_id} (Amount: ₹{amount:,.2f}).",
                evidence={"payment_id": payment_id, "amount": amount, "reason": "Exact duplicate refund attempt"}
            ))

        # Rule 2: Refund Abuse / High Frequency Refund Requests
        if recent_refunds_count >= 3:
            alerts.append(FraudAlertDomain(
                transaction_id=payment_id,
                customer_id=customer_id,
                alert_type=FraudAlertType.REFUND_ABUSE,
                severity=FraudSeverity.CRITICAL if recent_refunds_count >= 5 else FraudSeverity.HIGH,
                description=f"Refund abuse pattern flagged: Customer {customer_id} requested {recent_refunds_count} refunds within a short timeframe.",
                evidence={"customer_id": customer_id, "recent_refunds_count": recent_refunds_count}
            ))

        return alerts

    @staticmethod
    def inspect_daily_refund_spike(today_refund_sum: float, avg_daily_refund_sum: float) -> List[FraudAlertDomain]:
        alerts: List[FraudAlertDomain] = []

        if avg_daily_refund_sum > 0 and today_refund_sum > (3.0 * avg_daily_refund_sum) and today_refund_sum > 10000.0:
            alerts.append(FraudAlertDomain(
                alert_type=FraudAlertType.REFUND_SPIKE,
                severity=FraudSeverity.CRITICAL,
                description=f"Sudden refund spike detected! Today's refunds (₹{today_refund_sum:,.2f}) exceed 3x average baseline (₹{avg_daily_refund_sum:,.2f}).",
                evidence={"today_refund_sum": today_refund_sum, "baseline_avg": avg_daily_refund_sum, "spike_ratio": round(today_refund_sum / avg_daily_refund_sum, 2)}
            ))

        return alerts
