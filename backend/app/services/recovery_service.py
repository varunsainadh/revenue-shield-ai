import json
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.recovery_case_model import RecoveryCaseModel
from app.models.promise_to_pay_model import PromiseToPayModel
from app.models.outcome_model import RecoveryOutcomeModel
from app.models.settings_model import SettingsModel
from app.domain.enums import CaseState, AuditEventType, PTPStatus, FailureReason
from app.domain.recovery_case import validate_state_transition, classify_failure_reason
from app.domain.promise_to_pay import validate_ptp_transition
from app.agents.recovery_agent import RecoveryAgent
from app.services.audit_service import AuditService
from app.services.payment_link_service import PaymentLinkService

class RecoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_agent = RecoveryAgent()

    def get_merchant_settings(self) -> Dict[str, Any]:
        s = self.db.query(SettingsModel).filter(SettingsModel.id == 1).first()
        if not s:
            s = SettingsModel()
            self.db.add(s)
            self.db.commit()
            self.db.refresh(s)
        return {
            "auto_recovery_enabled": s.auto_recovery_enabled,
            "max_attempts": s.max_attempts,
            "recovery_window_hours": s.recovery_window_hours,
            "high_value_threshold": s.high_value_threshold,
            "quiet_hours_start": s.quiet_hours_start,
            "quiet_hours_end": s.quiet_hours_end,
            "voice_enabled": s.voice_enabled,
            "whatsapp_enabled": s.whatsapp_enabled,
            "email_enabled": s.email_enabled,
            "merchant_timezone": s.merchant_timezone
        }

    def create_case(self, case_data: Dict[str, Any]) -> RecoveryCaseModel:
        # Check if case for transaction already exists
        existing = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.transaction_id == case_data["transaction_id"]).first()
        if existing:
            return existing

        category = classify_failure_reason(case_data.get("failure_reason", "unknown"))

        new_case = RecoveryCaseModel(
            transaction_id=case_data["transaction_id"],
            customer_id=case_data["customer_id"],
            customer_email=case_data.get("customer_email", f"{case_data['customer_id']}@example.com"),
            customer_phone=case_data.get("customer_phone", "+919876543210"),
            amount=case_data["amount"],
            currency=case_data.get("currency", "INR"),
            payment_method=case_data.get("payment_method", "UPI"),
            bank=case_data.get("bank", "HDFC"),
            hour_of_day=case_data.get("hour_of_day", datetime.utcnow().hour),
            day_of_week=case_data.get("day_of_week", datetime.utcnow().weekday()),
            failure_reason=case_data["failure_reason"],
            failure_category=category.value,
            previous_success_count=case_data.get("previous_success_count", 0),
            previous_failure_count=case_data.get("previous_failure_count", 0),
            customer_success_rate=case_data.get("customer_success_rate", 0.5),
            attempt_number=0,
            max_attempts=case_data.get("max_attempts", 3),
            gateway_latency_ms=case_data.get("gateway_latency_ms", 200),
            device_type=case_data.get("device_type", "mobile"),
            risk_level=case_data.get("risk_level", "LOW"),
            status=CaseState.OPEN.value
        )
        self.db.add(new_case)
        self.db.commit()
        self.db.refresh(new_case)

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.CASE_CREATED,
            action="Recovery case created from payment failure event",
            case_id=new_case.id,
            new_state=CaseState.OPEN.value,
            metadata={"transaction_id": new_case.transaction_id, "amount": new_case.amount}
        )

        return new_case

    def analyze_case(self, case_id: str) -> RecoveryCaseModel:
        case = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Check state transition: -> ANALYZING
        validate_state_transition(CaseState(case.status), CaseState.ANALYZING)
        prev_state = case.status
        case.status = CaseState.ANALYZING.value
        self.db.commit()

        # Check for active Promise-to-Pay for customer
        active_ptp = (
            self.db.query(PromiseToPayModel)
            .filter(PromiseToPayModel.customer_id == case.customer_id, PromiseToPayModel.status == PTPStatus.ACTIVE.value)
            .first()
        )
        has_ptp = active_ptp is not None
        ptp_date = active_ptp.promised_date if active_ptp else None

        settings_dict = self.get_merchant_settings()

        case_dict = {
            "amount": case.amount,
            "failure_reason": case.failure_reason,
            "failure_category": case.failure_category,
            "customer_success_rate": case.customer_success_rate,
            "attempt_number": case.attempt_number,
            "risk_level": case.risk_level,
            "device_type": case.device_type,
            "created_at": case.created_at,
            "last_attempt_at": case.last_attempt_at,
            "status": case.status
        }

        # Log ML Scoring Started
        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.ML_SCORING_STARTED,
            action=f"Initiating ML recovery scoring and ERV estimation for case {case.id}",
            case_id=case.id
        )

        # Run AI Recovery Agent (ML Predictor + Policy Engine + Reasoner)
        try:
            rec = self.recovery_agent.analyze(case_dict, has_active_ptp=has_ptp, settings_override=settings_dict)
            
            AuditService.log_event(
                db=self.db,
                event_type=AuditEventType.ML_SCORE_GENERATED,
                action="ML model predicted channel recovery probabilities",
                case_id=case.id,
                metadata={k: v.probability for k, v in rec.channel_scores.items()}
            )
            
            AuditService.log_event(
                db=self.db,
                event_type=AuditEventType.ERV_CALCULATED,
                action="Calculated Expected Recovery Value across channels",
                case_id=case.id,
                metadata={k: v.erv for k, v in rec.channel_scores.items()}
            )
            
            AuditService.log_event(
                db=self.db,
                event_type=AuditEventType.CHANNEL_RECOMMENDED,
                action=f"Recommended recovery channel: {rec.recommended_channel}",
                case_id=case.id,
                confidence=rec.confidence
            )
        except Exception as err:
            AuditService.log_event(
                db=self.db,
                event_type=AuditEventType.ML_SCORING_FAILED,
                action=f"ML Scoring failed: {err}",
                case_id=case.id
            )
            raise err

        case.recoverability_score = rec.recoverability_score
        case.recommended_channel = rec.recommended_channel
        case.recommended_action = rec.recommended_action
        
        # Calculate selected ERV
        ch_lower = rec.recommended_channel.lower()
        sel_erv = rec.channel_scores.get(ch_lower, list(rec.channel_scores.values())[0]).erv
        case.recommended_erv = sel_erv

        case.channel_scores_json = json.dumps({k: v.model_dump() for k, v in rec.channel_scores.items()})
        case.policy_result = rec.policy_result
        case.policy_reason = rec.policy_reason
        case.ai_reasoning = rec.reason

        # Determine target state
        if rec.recommended_action == "MANUAL_REVIEW_REQUIRED" or rec.policy_result == "MANUAL_REVIEW":
            target_state = CaseState.MANUAL_REVIEW
        elif rec.recommended_action == "DO_NOT_RETRY" or rec.policy_result == "BLOCK":
            target_state = CaseState.STOPPED
        else:
            target_state = CaseState.ACTION_READY

        validate_state_transition(CaseState.ANALYZING, target_state)
        case.status = target_state.value
        self.db.commit()
        self.db.refresh(case)

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.AI_RECOMMENDATION_CREATED,
            action=f"AI Agent recommendation: {rec.recommended_action} via {rec.recommended_channel}",
            case_id=case.id,
            previous_state=prev_state,
            new_state=case.status,
            reason=rec.reason,
            confidence=rec.confidence,
            policy_rule=rec.policy_reason,
            metadata={"policy_result": rec.policy_result, "erv": sel_erv}
        )

        return case

    def execute_recovery(self, case_id: str) -> Dict[str, Any]:
        case = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        current_st = CaseState(case.status)
        if current_st == CaseState.OPEN:
            case = self.analyze_case(case_id)
            current_st = CaseState(case.status)

        if current_st in [CaseState.MANUAL_REVIEW, CaseState.STOPPED, CaseState.RECOVERED, CaseState.FAILED]:
            return {
                "status": case.status,
                "executed": False,
                "message": f"Execution halted because case status is '{case.status}'."
            }

        # Transition -> PENDING_RECOVERY
        validate_state_transition(current_st, CaseState.PENDING_RECOVERY)
        case.status = CaseState.PENDING_RECOVERY.value
        case.attempt_number += 1
        case.last_attempt_at = datetime.utcnow()
        self.db.commit()

        # Step 1: Create payment link
        plink = PaymentLinkService.get_or_create_payment_link(self.db, case)

        # Step 2: Transition -> WAITING_PAYMENT
        validate_state_transition(CaseState.PENDING_RECOVERY, CaseState.WAITING_PAYMENT)
        case.status = CaseState.WAITING_PAYMENT.value
        self.db.commit()
        self.db.refresh(case)

        # Dispatch via LiveOutreachService (gated behind LIVE_OUTREACH_ENABLED)
        from app.services.live_outreach_service import LiveOutreachService
        channel_to_use = (case.recommended_channel or "WHATSAPP").upper()
        if channel_to_use == "EMAIL":
            outreach_res = LiveOutreachService.send_email(
                to_email=f"{case.customer_id}@example.com",
                customer_name=case.customer_id,
                amount=case.amount,
                failure_reason=case.failure_reason,
                payment_link_url=plink.url,
                case_id=case.id
            )
        elif channel_to_use == "VOICE":
            outreach_res = LiveOutreachService.initiate_voice_call(
                to_phone="+919876543210",
                customer_name=case.customer_id,
                amount=case.amount,
                failure_reason=case.failure_reason,
                payment_link_url=plink.url,
                case_id=case.id
            )
        else:
            outreach_res = LiveOutreachService.send_whatsapp(
                to_phone="+919876543210",
                customer_name=case.customer_id,
                amount=case.amount,
                failure_reason=case.failure_reason,
                payment_link_url=plink.url,
                case_id=case.id
            )

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.RECOVERY_MESSAGE_SENT,
            action=f"Recovery intervention sent via {channel_to_use} (Status: {outreach_res.get('status')})",
            case_id=case.id,
            previous_state=CaseState.PENDING_RECOVERY.value,
            new_state=CaseState.WAITING_PAYMENT.value,
            metadata={
                "payment_link_url": plink.url, 
                "channel": channel_to_use, 
                "attempt": case.attempt_number,
                "outreach_status": outreach_res.get("status")
            }
        )

        return {
            "status": case.status,
            "executed": True,
            "channel": channel_to_use,
            "payment_link_url": plink.url,
            "attempt_number": case.attempt_number,
            "outreach_status": outreach_res.get("status")
        }

    def process_payment_success(self, case_id: str, channel_override: Optional[str] = None) -> RecoveryCaseModel:
        case = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if case.status == CaseState.RECOVERED.value:
            return case # Idempotent: already recovered

        current_st = CaseState(case.status)
        
        # Valid state transition check
        if current_st not in [CaseState.PENDING_RECOVERY, CaseState.WAITING_PAYMENT, CaseState.ACTION_READY, CaseState.MANUAL_REVIEW, CaseState.OPEN, CaseState.ANALYZING]:
            raise ValueError(f"Cannot recover case from state {case.status}")

        case.status = CaseState.RECOVERED.value
        case.recovered_at = datetime.utcnow()
        self.db.commit()

        # Record outcome
        time_to_recover = round((case.recovered_at - case.created_at).total_seconds() / 60.0, 2)
        outcome = RecoveryOutcomeModel(
            recovery_case_id=case.id,
            recovered=True,
            recovered_amount=case.amount,
            channel_used=channel_override or case.recommended_channel or "WHATSAPP",
            time_to_recover_minutes=time_to_recover,
            attempts_count=max(1, case.attempt_number)
        )
        self.db.add(outcome)
        self.db.commit()
        self.db.refresh(case)

        # Audit event
        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.REVENUE_RECOVERED,
            action=f"Payment successfully recovered for ₹{case.amount:,.2f}",
            case_id=case.id,
            previous_state=current_st.value,
            new_state=CaseState.RECOVERED.value,
            reason="Customer completed recovery payment",
            metadata={"recovered_amount": case.amount, "channel_used": outcome.channel_used}
        )

        return case

    def manual_approve(self, case_id: str) -> RecoveryCaseModel:
        case = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if case.status != CaseState.MANUAL_REVIEW.value:
            raise ValueError(f"Case {case_id} is not in MANUAL_REVIEW state.")

        prev_st = case.status
        validate_state_transition(CaseState.MANUAL_REVIEW, CaseState.ACTION_READY)
        case.status = CaseState.ACTION_READY.value
        self.db.commit()

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.MANUAL_APPROVED,
            action="Merchant manually approved high-value / restricted recovery case",
            case_id=case.id,
            actor="MERCHANT_OPERATOR",
            previous_state=prev_st,
            new_state=case.status
        )

        # Trigger execution immediately after approval
        self.execute_recovery(case.id)
        return case

    def manual_reject(self, case_id: str, reason: str = "Rejected by merchant") -> RecoveryCaseModel:
        case = self.db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        prev_st = case.status
        validate_state_transition(CaseState(case.status), CaseState.STOPPED)
        case.status = CaseState.STOPPED.value
        self.db.commit()

        AuditService.log_event(
            db=self.db,
            event_type=AuditEventType.MANUAL_REJECTED,
            action="Merchant manually rejected recovery intervention",
            case_id=case.id,
            actor="MERCHANT_OPERATOR",
            previous_state=prev_st,
            new_state=case.status,
            reason=reason
        )
        return case
