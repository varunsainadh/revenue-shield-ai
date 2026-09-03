from datetime import datetime, time
import pytz
from typing import Optional, Dict, Any, Tuple
from app.domain.enums import PolicyResult, RecoveryChannel, RiskLevel

class PolicyDecision:
    def __init__(self, result: PolicyResult, reason: str, policy_name: str):
        self.result = result
        self.reason = reason
        self.policy_name = policy_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result.value,
            "reason": self.reason,
            "policy_name": self.policy_name
        }

class QuietHoursPolicy:
    @staticmethod
    def evaluate(channel: RecoveryChannel, current_time: datetime, timezone_str: str = "Asia/Kolkata", start_hour: int = 21, end_hour: int = 9) -> Optional[PolicyDecision]:
        try:
            tz = pytz.timezone(timezone_str)
            local_time = current_time.astimezone(tz) if current_time.tzinfo else pytz.utc.localize(current_time).astimezone(tz)
        except Exception:
            local_time = current_time

        hour = local_time.hour
        is_quiet = hour >= start_hour or hour < end_hour

        if is_quiet and channel == RecoveryChannel.VOICE:
            return PolicyDecision(
                PolicyResult.BLOCK,
                f"Voice calls are blocked during quiet hours ({start_hour}:00 to {end_hour:02d}:00 {timezone_str}).",
                "QuietHoursPolicy"
            )
        elif is_quiet and channel == RecoveryChannel.WHATSAPP:
            return PolicyDecision(
                PolicyResult.DELAY,
                f"WhatsApp outreach delayed until after quiet hours.",
                "QuietHoursPolicy"
            )
        return None

class MaximumAttemptsPolicy:
    @staticmethod
    def evaluate(attempt_number: int, max_attempts: int = 3) -> Optional[PolicyDecision]:
        if attempt_number >= max_attempts:
            return PolicyDecision(
                PolicyResult.BLOCK,
                f"Maximum recovery attempts ({max_attempts}) reached.",
                "MaximumAttemptsPolicy"
            )
        return None

class MaximumRecoveryWindowPolicy:
    @staticmethod
    def evaluate(created_at: datetime, max_window_hours: int = 72) -> Optional[PolicyDecision]:
        now = datetime.utcnow()
        hours_elapsed = (now - created_at).total_seconds() / 3600.0
        if hours_elapsed > max_window_hours:
            return PolicyDecision(
                PolicyResult.BLOCK,
                f"Maximum recovery window of {max_window_hours} hours exceeded.",
                "MaximumRecoveryWindowPolicy"
            )
        return None

class HighValueApprovalPolicy:
    @staticmethod
    def evaluate(amount: float, threshold: float = 15000.0) -> Optional[PolicyDecision]:
        if amount >= threshold:
            return PolicyDecision(
                PolicyResult.MANUAL_REVIEW,
                f"Amount ₹{amount:,.2f} exceeds high-value threshold (₹{threshold:,.2f}). Manual review required.",
                "HighValueApprovalPolicy"
            )
        return None

class ActivePromiseToPayPolicy:
    @staticmethod
    def evaluate(has_active_ptp: bool, promised_date: Optional[datetime] = None) -> Optional[PolicyDecision]:
        if has_active_ptp:
            promised_str = promised_date.strftime("%Y-%m-%d") if promised_date else "future date"
            return PolicyDecision(
                PolicyResult.DELAY,
                f"Customer has an active Promise-to-Pay scheduled for {promised_str}. Outreach suppressed.",
                "ActivePromiseToPayPolicy"
            )
        return None

class AlreadyRecoveredPolicy:
    @staticmethod
    def evaluate(status: str) -> Optional[PolicyDecision]:
        if status in ["RECOVERED", "RECOVERED_CONFIRMED"]:
            return PolicyDecision(
                PolicyResult.BLOCK,
                "Case is already recovered.",
                "AlreadyRecoveredPolicy"
            )
        return None

class FraudRiskPolicy:
    @staticmethod
    def evaluate(failure_reason: str, risk_level: str) -> Optional[PolicyDecision]:
        if failure_reason in ["fraud_suspected", "risk_declined"] or risk_level in ["HIGH", "CRITICAL"]:
            return PolicyDecision(
                PolicyResult.BLOCK,
                f"Blocked due to risk flag (Reason: {failure_reason}, Risk: {risk_level}). Automation stopped.",
                "FraudRiskPolicy"
            )
        return None

class CooldownPolicy:
    @staticmethod
    def evaluate(last_attempt_at: Optional[datetime], cooldown_minutes: int = 30) -> Optional[PolicyDecision]:
        if last_attempt_at:
            minutes_since = (datetime.utcnow() - last_attempt_at).total_seconds() / 60.0
            if minutes_since < cooldown_minutes:
                return PolicyDecision(
                    PolicyResult.DELAY,
                    f"Cooldown period active ({int(cooldown_minutes - minutes_since)} mins remaining).",
                    "CooldownPolicy"
                )
        return None
