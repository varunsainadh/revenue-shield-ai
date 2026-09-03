from typing import Dict, Any, Optional
from datetime import datetime
from app.domain.enums import PolicyResult, RecoveryChannel
from app.agents.guardrails import (
    PolicyDecision,
    AlreadyRecoveredPolicy,
    FraudRiskPolicy,
    MaximumAttemptsPolicy,
    MaximumRecoveryWindowPolicy,
    HighValueApprovalPolicy,
    ActivePromiseToPayPolicy,
    QuietHoursPolicy,
    CooldownPolicy
)

class PolicyService:
    def __init__(self, settings_obj=None):
        self.settings = settings_obj

    def validate_action(
        self,
        case_data: Dict[str, Any],
        proposed_channel: str,
        has_active_ptp: bool = False,
        ptp_date: Optional[datetime] = None,
        settings_override: Optional[Dict[str, Any]] = None
    ) -> PolicyDecision:
        
        # Merge settings
        high_value_thresh = settings_override.get("high_value_threshold", 15000.0) if settings_override else 15000.0
        max_attempts = settings_override.get("max_attempts", 3) if settings_override else 3
        max_window = settings_override.get("recovery_window_hours", 72) if settings_override else 72
        tz_str = settings_override.get("merchant_timezone", "Asia/Kolkata") if settings_override else "Asia/Kolkata"
        q_start = settings_override.get("quiet_hours_start", 21) if settings_override else 21
        q_end = settings_override.get("quiet_hours_end", 9) if settings_override else 9

        # Priority 1: Already recovered check
        decision = AlreadyRecoveredPolicy.evaluate(case_data.get("status", "OPEN"))
        if decision:
            return decision

        # Priority 2: Fraud / Severe Risk check
        decision = FraudRiskPolicy.evaluate(
            case_data.get("failure_reason", "unknown"),
            case_data.get("risk_level", "LOW")
        )
        if decision:
            return decision

        # Priority 3: Maximum attempts check
        decision = MaximumAttemptsPolicy.evaluate(
            case_data.get("attempt_number", 0),
            max_attempts=max_attempts
        )
        if decision:
            return decision

        # Priority 4: Maximum recovery window check
        created_at = case_data.get("created_at")
        if isinstance(created_at, datetime):
            decision = MaximumRecoveryWindowPolicy.evaluate(created_at, max_window_hours=max_window)
            if decision:
                return decision

        # Priority 5: Active Promise to Pay check
        decision = ActivePromiseToPayPolicy.evaluate(has_active_ptp, ptp_date)
        if decision:
            return decision

        # Priority 6: High value financial threshold check
        decision = HighValueApprovalPolicy.evaluate(
            float(case_data.get("amount", 0.0)),
            threshold=high_value_thresh
        )
        if decision:
            return decision

        # Priority 7: Quiet hours check
        try:
            ch_enum = RecoveryChannel(proposed_channel.upper())
            decision = QuietHoursPolicy.evaluate(
                ch_enum,
                current_time=datetime.utcnow(),
                timezone_str=tz_str,
                start_hour=q_start,
                end_hour=q_end
            )
            if decision:
                return decision
        except ValueError:
            pass

        # Priority 8: Cooldown check
        last_attempt = case_data.get("last_attempt_at")
        if isinstance(last_attempt, datetime):
            decision = CooldownPolicy.evaluate(last_attempt, cooldown_minutes=30)
            if decision:
                return decision

        # Default: ALLOW
        return PolicyDecision(
            PolicyResult.ALLOW,
            "Policy engine validated and approved recovery action.",
            "DefaultApproval"
        )
