from typing import Dict, Any
from app.domain.recovery_case import classify_failure_reason
from app.domain.enums import FailureCategory, RecoveryChannel, RecoveryActionType, RiskLevel

# Simulated costs per channel intervention in INR
SIMULATED_CHANNEL_COSTS = {
    RecoveryChannel.EMAIL: 2.0,
    RecoveryChannel.WHATSAPP: 5.0,
    RecoveryChannel.VOICE: 15.0
}

class DeterministicReasoner:
    @staticmethod
    def calculate_channel_scores(
        amount: float,
        failure_reason: str,
        customer_success_rate: float = 0.5,
        risk_level: str = "LOW",
        device_type: str = "mobile"
    ) -> Dict[str, Dict[str, float]]:
        
        category = classify_failure_reason(failure_reason)

        if risk_level in ["HIGH", "CRITICAL"] or failure_reason == "fraud_suspected":
            p_email, p_wa, p_voice = 0.05, 0.02, 0.01
        elif category == FailureCategory.CUSTOMER_CORRECTABLE:
            p_email = min(0.95, 0.55 + customer_success_rate * 0.3)
            p_wa = min(0.98, 0.70 + customer_success_rate * 0.25)
            p_voice = min(0.90, 0.50 + customer_success_rate * 0.3)
        elif category == FailureCategory.INSUFFICIENT_FUNDS:
            p_email = min(0.70, 0.30 + customer_success_rate * 0.3)
            p_wa = min(0.85, 0.45 + customer_success_rate * 0.35)
            p_voice = min(0.60, 0.25 + customer_success_rate * 0.3)
        elif category == FailureCategory.TEMPORARY_INFRASTRUCTURE:
            p_email = 0.75
            p_wa = 0.90
            p_voice = 0.60
        elif category == FailureCategory.PAYMENT_METHOD_PROBLEM:
            p_email = 0.60
            p_wa = 0.78
            p_voice = 0.50
        else:
            p_email, p_wa, p_voice = 0.30, 0.40, 0.25

        if "mobile" in device_type:
            p_wa = min(0.99, p_wa + 0.08)

        email_erv = round(p_email * amount, 2)
        wa_erv = round(p_wa * amount, 2)
        voice_erv = round(p_voice * amount, 2)

        return {
            "email": {
                "probability": round(p_email, 2),
                "erv": email_erv,
                "simulated_cost": SIMULATED_CHANNEL_COSTS[RecoveryChannel.EMAIL]
            },
            "whatsapp": {
                "probability": round(p_wa, 2),
                "erv": wa_erv,
                "simulated_cost": SIMULATED_CHANNEL_COSTS[RecoveryChannel.WHATSAPP]
            },
            "voice": {
                "probability": round(p_voice, 2),
                "erv": voice_erv,
                "simulated_cost": SIMULATED_CHANNEL_COSTS[RecoveryChannel.VOICE]
            }
        }

    @classmethod
    def evaluate(cls, case_data: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(case_data.get("amount", 0.0))
        failure_reason = case_data.get("failure_reason", "unknown")
        success_rate = float(case_data.get("customer_success_rate", 0.5))
        risk_level = case_data.get("risk_level", "LOW")
        device = case_data.get("device_type", "mobile")

        category = classify_failure_reason(failure_reason)
        scores = cls.calculate_channel_scores(amount, failure_reason, success_rate, risk_level, device)

        # Select highest net ERV candidate (erv - cost)
        best_channel = "whatsapp"
        best_net_erv = -999999.0
        for ch, sc in scores.items():
            net_erv = sc["erv"] - sc["simulated_cost"]
            if net_erv > best_net_erv:
                best_net_erv = net_erv
                best_channel = ch

        best_score = scores[best_channel]
        rec_channel = best_channel.upper()

        if failure_reason in ["fraud_suspected", "risk_declined"] or risk_level in ["HIGH", "CRITICAL"]:
            action = RecoveryActionType.DO_NOT_RETRY.value
            confidence = 0.95
            reason = f"High risk flag ({risk_level}) or fraud suspicion detected. Retries blocked to prevent fraud."
        elif category == FailureCategory.TEMPORARY_INFRASTRUCTURE:
            action = RecoveryActionType.WAIT_AND_RETRY.value
            confidence = 0.88
            reason = f"Failure due to bank or gateway downtime. Delay outreach until infrastructure stabilizes."
        else:
            action = RecoveryActionType.SEND_PAYMENT_LINK.value
            confidence = round(best_score["probability"], 2)
            reason = (
                f"{rec_channel} selected because past customer recovery patterns and failure category "
                f"({category.value}) produced highest Expected Recovery Value (₹{best_score['erv']:,.2f})."
            )

        overall_recoverability = round(max(s["probability"] for s in scores.values()), 2)

        return {
            "failure_category": category.value,
            "recoverability_score": overall_recoverability,
            "channel_scores": scores,
            "recommended_channel": rec_channel,
            "recommended_action": action,
            "confidence": confidence,
            "risk_level": risk_level,
            "reason": reason
        }

    @staticmethod
    def parse_hinglish_voice_intent(user_transcript: str) -> Dict[str, Any]:
        """
        Priority 7 (Track 03): Hinglish Code-Switching Voice Recovery Parser.
        Parses spoken Hinglish customer responses into structured recovery intents and PTP dates.
        """
        text = user_transcript.lower()

        intent = "UNKNOWN"
        ptp_days = None
        extracted_reason = None

        # PTP & Schedule Promises
        if any(w in text for w in ["friday", "kal", "tomorrow", "parso", "subah", "shaam", "pay kar dunga", "pay kar dungi", "payment kar dunga", "kardoonga"]):
            intent = "PROMISE_TO_PAY"
            if "friday" in text:
                ptp_days = 2
            elif "parso" in text:
                ptp_days = 2
            else:
                ptp_days = 1

        # Failure Intent Clarification
        if any(w in text for w in ["passcode", "pin galat", "incorrect pin", "pin bhool gaya"]):
            extracted_reason = "incorrect_pin"
        elif any(w in text for w in ["server down", "bank down", "server issue"]):
            extracted_reason = "bank_down"
        elif any(w in text for w in ["balance nahi hai", "paisa nahi hai", "low balance", "paise nahi"]):
            extracted_reason = "insufficient_funds"

        return {
            "transcript": user_transcript,
            "intent": intent,
            "ptp_delay_days": ptp_days,
            "extracted_reason": extracted_reason,
            "parsed_hinglish": True
        }

