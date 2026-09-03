import json
from typing import Dict, Any, Optional
from app.services.scoring_service import ScoringService
from app.agents.llm_reasoner import LLMReasoner
from app.services.policy_service import PolicyService
from app.schemas.recovery import AgentRecommendation, ChannelScoreDetail

class RecoveryAgent:
    def __init__(self, policy_service: Optional[PolicyService] = None):
        self.policy_service = policy_service or PolicyService()

    def analyze(
        self,
        case_data: Dict[str, Any],
        has_active_ptp: bool = False,
        settings_override: Optional[Dict[str, Any]] = None
    ) -> AgentRecommendation:
        
        # Step 1: ML Predictor & ERV Scoring
        raw_eval = ScoringService.get_predictions(case_data)

        channel_scores = {
            k: ChannelScoreDetail(**v) for k, v in raw_eval["channel_scores"].items()
        }

        recommended_ch = raw_eval["recommended_channel"]

        # Step 2: Policy & Guardrail Engine validation
        policy_decision = self.policy_service.validate_action(
            case_data=case_data,
            proposed_channel=recommended_ch,
            has_active_ptp=has_active_ptp,
            settings_override=settings_override
        )

        final_policy_result = policy_decision.result.value
        final_policy_reason = policy_decision.reason

        # Override recommended action if policy blocks or mandates manual review
        final_action = raw_eval["recommended_action"]
        if policy_decision.result.value == "MANUAL_REVIEW":
            final_action = "MANUAL_REVIEW_REQUIRED"
        elif policy_decision.result.value == "BLOCK":
            final_action = "DO_NOT_RETRY"
        elif policy_decision.result.value == "DELAY":
            final_action = "WAIT_AND_RETRY"

        # Step 3: Explanation generation (LLM if available, else deterministic)
        explanation = LLMReasoner.generate_explanation(
            case_data=case_data,
            recommendation=raw_eval,
            fallback_reason=raw_eval["reason"]
        )

        return AgentRecommendation(
            failure_category=raw_eval["failure_category"],
            recoverability_score=raw_eval["recoverability_score"],
            channel_scores=channel_scores,
            recommended_channel=recommended_ch,
            recommended_action=final_action,
            confidence=raw_eval["confidence"],
            risk_level=raw_eval["risk_level"],
            reason=explanation,
            policy_result=final_policy_result,
            policy_reason=final_policy_reason
        )
