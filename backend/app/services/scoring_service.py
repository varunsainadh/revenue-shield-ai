import os
from typing import Dict, Any
from app.ml.predictor import MLPredictor
from app.agents.deterministic_reasoner import DeterministicReasoner, SIMULATED_CHANNEL_COSTS
from app.domain.recovery_case import classify_failure_reason
from app.domain.enums import FailureCategory, RecoveryChannel, RecoveryActionType

class ScoringService:
    @staticmethod
    def get_predictions(case_data: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(case_data.get("amount", 0.0))
        failure_reason = case_data.get("failure_reason", "unknown")
        risk_level = case_data.get("risk_level", "LOW")

        # Try ML Predictor inference
        try:
            if MLPredictor.is_trained():
                probs = MLPredictor.predict_channel_probabilities(case_data)
                
                # Check for high risk / fraud suspicion to override probabilities safely
                category = classify_failure_reason(failure_reason)
                if failure_reason in ["fraud_suspected", "risk_declined"] or risk_level in ["HIGH", "CRITICAL"]:
                    probs = {"email": 0.02, "whatsapp": 0.01, "voice": 0.01}

                channel_scores = {}
                for ch_name, p in probs.items():
                    ch_enum = RecoveryChannel(ch_name.upper())
                    cost = SIMULATED_CHANNEL_COSTS[ch_enum]
                    erv = round(p * amount, 2)
                    channel_scores[ch_name] = {
                        "probability": p,
                        "erv": erv,
                        "simulated_cost": cost
                    }

                # Select recommended channel based on highest Net ERV (ERV - cost)
                best_channel = "whatsapp"
                best_net_erv = -999999.0
                for ch, sc in channel_scores.items():
                    net_erv = sc["erv"] - sc["simulated_cost"]
                    if net_erv > best_net_erv:
                        best_net_erv = net_erv
                        best_channel = ch

                best_score = channel_scores[best_channel]
                rec_channel = best_channel.upper()

                if failure_reason in ["fraud_suspected", "risk_declined"] or risk_level in ["HIGH", "CRITICAL"]:
                    action = RecoveryActionType.DO_NOT_RETRY.value
                    confidence = 0.95
                    reason = f"High risk flag ({risk_level}) or fraud suspicion. ML retries blocked."
                elif category == FailureCategory.TEMPORARY_INFRASTRUCTURE:
                    action = RecoveryActionType.WAIT_AND_RETRY.value
                    confidence = 0.88
                    reason = f"Temporary bank/gateway infrastructure downtime ({failure_reason}). Delay outreach."
                else:
                    action = RecoveryActionType.SEND_PAYMENT_LINK.value
                    confidence = round(best_score["probability"], 2)
                    reason = (
                        f"ML Model selected {rec_channel} with {best_score['probability']*100:.1f}% recovery probability "
                        f"and Expected Recovery Value of ₹{best_score['erv']:,.2f}."
                    )

                overall_recoverability = round(max(s["probability"] for s in channel_scores.values()), 2)

                return {
                    "failure_category": category.value,
                    "recoverability_score": overall_recoverability,
                    "channel_scores": channel_scores,
                    "recommended_channel": rec_channel,
                    "recommended_action": action,
                    "confidence": confidence,
                    "risk_level": risk_level,
                    "reason": reason
                }
        except Exception as e:
            # Fallback seamlessly to deterministic engine
            pass

        return DeterministicReasoner.evaluate(case_data)
