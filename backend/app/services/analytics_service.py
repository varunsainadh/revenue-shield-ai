from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.models.recovery_case_model import RecoveryCaseModel
from app.models.outcome_model import RecoveryOutcomeModel
from app.schemas.analytics import MetricsSummary, AnalyticsData

class AnalyticsService:
    @staticmethod
    def get_metrics_summary(db: Session) -> MetricsSummary:
        total_tx = db.query(RecoveryCaseModel).count()
        if total_tx == 0:
            return MetricsSummary(
                total_transactions=0,
                failed_transactions=0,
                revenue_at_risk=0.0,
                recovered_revenue=0.0,
                net_recovered_revenue=0.0,
                recovery_rate=0.0,
                recovery_efficiency=0.0,
                active_recovery_cases=0,
                recovered_cases=0,
                manual_reviews=0,
                blocked_cases=0,
                top_performing_channel="WHATSAPP"
            )

        failed_tx = total_tx
        rev_at_risk = db.query(func.sum(RecoveryCaseModel.amount)).scalar() or 0.0
        
        recovered_cases_cnt = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status == "RECOVERED").count()
        rec_revenue = db.query(func.sum(RecoveryCaseModel.amount)).filter(RecoveryCaseModel.status == "RECOVERED").scalar() or 0.0

        active_cases_cnt = db.query(RecoveryCaseModel).filter(
            RecoveryCaseModel.status.in_(["OPEN", "ANALYZING", "ACTION_READY", "PENDING_RECOVERY", "WAITING_PAYMENT"])
        ).count()

        manual_rev_cnt = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status == "MANUAL_REVIEW").count()
        blocked_cnt = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status.in_(["STOPPED", "FAILED"])).count()

        rec_rate = round((recovered_cases_cnt / total_tx) * 100.0, 1) if total_tx > 0 else 0.0
        rec_eff = round((rec_revenue / rev_at_risk) * 100.0, 1) if rev_at_risk > 0 else 0.0

        # Channel breakdown for top performing channel
        top_ch_query = (
            db.query(RecoveryOutcomeModel.channel_used, func.sum(RecoveryOutcomeModel.recovered_amount).label("sum_amt"))
            .filter(RecoveryOutcomeModel.recovered == True)
            .group_by(RecoveryOutcomeModel.channel_used)
            .order_by(func.sum(RecoveryOutcomeModel.recovered_amount).desc())
            .first()
        )
        top_ch = top_ch_query[0] if top_ch_query and top_ch_query[0] else "WHATSAPP"

        # Estimated total intervention cost
        net_rec = rec_revenue * 0.96 # approx simulated intervention cost deduction

        return MetricsSummary(
            total_transactions=total_tx,
            failed_transactions=failed_tx,
            revenue_at_risk=round(rev_at_risk, 2),
            recovered_revenue=round(rec_revenue, 2),
            net_recovered_revenue=round(net_rec, 2),
            recovery_rate=rec_rate,
            recovery_efficiency=rec_eff,
            active_recovery_cases=active_cases_cnt,
            recovered_cases=recovered_cases_cnt,
            manual_reviews=manual_rev_cnt,
            blocked_cases=blocked_cnt,
            top_performing_channel=top_ch
        )

    @staticmethod
    def get_analytics_data(db: Session) -> AnalyticsData:
        summary = AnalyticsService.get_metrics_summary(db)

        # 1. Recovery Funnel
        total_tx = summary.total_transactions
        eligible = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status != "STOPPED").count()
        action_sent = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.attempt_number > 0).count()
        waiting = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status.in_(["WAITING_PAYMENT", "RECOVERED"])).count()
        recovered = summary.recovered_cases

        funnel = [
            {"stage": "Payment Failed", "count": total_tx, "conversion": 100.0},
            {"stage": "Case Created", "count": total_tx, "conversion": 100.0},
            {"stage": "Eligible for Recovery", "count": eligible, "conversion": round((eligible / total_tx * 100) if total_tx else 0, 1)},
            {"stage": "Action Sent", "count": action_sent, "conversion": round((action_sent / total_tx * 100) if total_tx else 0, 1)},
            {"stage": "Customer Engaged", "count": waiting, "conversion": round((waiting / total_tx * 100) if total_tx else 0, 1)},
            {"stage": "Revenue Recovered", "count": recovered, "conversion": summary.recovery_rate}
        ]

        # 2. Failure Reasons Breakdown
        reasons_q = (
            db.query(RecoveryCaseModel.failure_reason, func.count(RecoveryCaseModel.id), func.sum(RecoveryCaseModel.amount))
            .group_by(RecoveryCaseModel.failure_reason)
            .all()
        )
        failure_reasons = [
            {"reason": r[0], "count": r[1], "amount_at_risk": round(r[2] or 0.0, 2)}
            for r in reasons_q
        ]

        # 3. Channel Performance
        ch_q = (
            db.query(
                RecoveryOutcomeModel.channel_used,
                func.count(RecoveryOutcomeModel.id).label("total"),
                func.sum(RecoveryOutcomeModel.recovered_amount).label("recovered_sum")
            )
            .filter(RecoveryOutcomeModel.recovered == True)
            .group_by(RecoveryOutcomeModel.channel_used)
            .all()
        )
        channel_performance = [
            {"channel": c[0] or "WHATSAPP", "recoveries": c[1], "recovered_amount": round(c[2] or 0.0, 2)}
            for c in ch_q
        ]
        if not channel_performance:
            channel_performance = [
                {"channel": "WHATSAPP", "recoveries": 0, "recovered_amount": 0.0},
                {"channel": "EMAIL", "recoveries": 0, "recovered_amount": 0.0},
                {"channel": "VOICE", "recoveries": 0, "recovered_amount": 0.0}
            ]

        # 4. Revenue Trend (Simulated 7-day or 12-hour buckets)
        revenue_trend = [
            {"day": "Mon", "at_risk": summary.revenue_at_risk * 0.14, "recovered": summary.recovered_revenue * 0.15},
            {"day": "Tue", "at_risk": summary.revenue_at_risk * 0.16, "recovered": summary.recovered_revenue * 0.14},
            {"day": "Wed", "at_risk": summary.revenue_at_risk * 0.18, "recovered": summary.recovered_revenue * 0.18},
            {"day": "Thu", "at_risk": summary.revenue_at_risk * 0.15, "recovered": summary.recovered_revenue * 0.16},
            {"day": "Fri", "at_risk": summary.revenue_at_risk * 0.12, "recovered": summary.recovered_revenue * 0.13},
            {"day": "Sat", "at_risk": summary.revenue_at_risk * 0.13, "recovered": summary.recovered_revenue * 0.12},
            {"day": "Sun", "at_risk": summary.revenue_at_risk * 0.12, "recovered": summary.recovered_revenue * 0.12},
        ]

        return AnalyticsData(
            metrics=summary,
            revenue_trend=revenue_trend,
            funnel=funnel,
            channel_performance=channel_performance,
            failure_reasons=failure_reasons
        )
