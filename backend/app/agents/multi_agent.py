from typing import Dict, Any, List, Optional
from app.ml.chargeback_model import ChargebackPredictor
from app.ml.fraud_detector import FraudDetector
from app.agents.recovery_agent import RecoveryAgent
from app.agents.copilot_agent import CopilotAgent
from app.domain.chargeback import ChargebackPredictionDomain
from app.domain.fraud import FraudAlertDomain
from app.schemas.recovery import AgentRecommendation

class FraudAgent:
    @staticmethod
    def analyze_refund(payment_id: str, customer_id: str, amount: float, recent_count: int = 0, is_dup: bool = False) -> List[FraudAlertDomain]:
        return FraudDetector.inspect_refund_event(payment_id, customer_id, amount, recent_count, is_dup)

class ChargebackAgent:
    @staticmethod
    def predict_dispute_risk(tx_data: Dict[str, Any]) -> ChargebackPredictionDomain:
        return ChargebackPredictor.predict_risk(tx_data)

class MultiAgentOrchestrator:
    def __init__(self):
        self.fraud_agent = FraudAgent()
        self.chargeback_agent = ChargebackAgent()
        self.recovery_agent = RecoveryAgent()
        self.copilot_agent = CopilotAgent()

    def process_transaction_event(self, tx_data: Dict[str, Any], settings_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # 1. Chargeback Risk Scoring
        cb_pred = self.chargeback_agent.predict_dispute_risk(tx_data)

        # 2. Recovery Analysis (if failed transaction)
        rec_recommendation = None
        if tx_data.get("failure_reason"):
            rec_recommendation = self.recovery_agent.analyze(
                case_data=tx_data,
                settings_override=settings_override
            )

        return {
            "chargeback_prediction": cb_pred,
            "recovery_recommendation": rec_recommendation
        }
