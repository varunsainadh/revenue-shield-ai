import json
from typing import Dict, Any, List
from app.domain.enums import RiskLevel
from app.domain.chargeback import ChargebackFactor, ChargebackPredictionDomain

class ChargebackPredictor:
    @staticmethod
    def predict_risk(tx_data: Dict[str, Any]) -> ChargebackPredictionDomain:
        amount = float(tx_data.get("amount", 0.0))
        prev_fails = int(tx_data.get("previous_failure_count", 0))
        is_first_time = bool(tx_data.get("is_first_time_customer", False))
        failure_reason = str(tx_data.get("failure_reason", "unknown"))
        risk_flag = str(tx_data.get("risk_level", "LOW")).upper()

        risk_score = 15 # Base baseline risk score
        risk_factors: List[ChargebackFactor] = []

        # Factor 1: First-time customer
        if is_first_time or int(tx_data.get("previous_success_count", 0)) == 0:
            risk_score += 25
            risk_factors.append(ChargebackFactor(
                factor="First-time Customer",
                impact="HIGH",
                description="New customer profile with no established transaction history on the platform."
            ))

        # Factor 2: High transaction value
        if amount >= 15000.0:
            risk_score += 30
            risk_factors.append(ChargebackFactor(
                factor="High Transaction Value",
                impact="HIGH",
                description=f"Transaction amount (₹{amount:,.2f}) significantly exceeds standard payment average."
            ))
        elif amount >= 5000.0:
            risk_score += 15
            risk_factors.append(ChargebackFactor(
                factor="Elevated Transaction Amount",
                impact="MEDIUM",
                description=f"Above-average transaction value of ₹{amount:,.2f}."
            ))

        # Factor 3: Multiple failed payment attempts
        if prev_fails >= 2:
            risk_score += 20
            risk_factors.append(ChargebackFactor(
                factor="Multiple Failed Attempts",
                impact="MEDIUM",
                description=f"Customer experienced {prev_fails} failed payment attempts prior to this order."
            ))

        # Factor 4: Unusual purchase pattern or risk decline
        if failure_reason in ["fraud_suspected", "risk_declined"] or risk_flag in ["HIGH", "CRITICAL"]:
            risk_score += 35
            risk_factors.append(ChargebackFactor(
                factor="Unusual Purchase Pattern / Risk Flag",
                impact="HIGH",
                description=f"Gateway risk indicator triggered (Reason: {failure_reason}, Level: {risk_flag})."
            ))

        # Clamp risk score between 5 and 99
        final_score = max(5, min(99, risk_score))

        if final_score >= 80:
            level = RiskLevel.CRITICAL
        elif final_score >= 60:
            level = RiskLevel.HIGH
        elif final_score >= 35:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # Generate human-readable explanation summary
        factor_titles = [f.factor for f in risk_factors]
        if factor_titles:
            explanation = f"Risk Score of {final_score}% driven by: {', '.join(factor_titles)}."
        else:
            explanation = f"Low chargeback risk score ({final_score}%) with standard customer transaction history."

        return ChargebackPredictionDomain(
            transaction_id=str(tx_data.get("transaction_id", "tx_unknown")),
            customer_id=str(tx_data.get("customer_id", "cust_unknown")),
            amount=amount,
            risk_score=final_score,
            risk_level=level,
            confidence=0.88,
            top_risk_factors=risk_factors,
            explanation=explanation
        )
