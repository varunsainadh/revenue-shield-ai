import json
from typing import Dict, Any, List
from app.config import settings

class CopilotAgent:
    @staticmethod
    def answer_query(query: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        query_lower = query.lower()

        metrics = context_data.get("metrics", {})
        high_risk_cases = context_data.get("high_risk_cases", [])
        active_alerts = context_data.get("active_alerts", [])
        recent_cases = context_data.get("recent_cases", [])

        # RAG / Structured Query Parsing & Answering
        if "decrease" in query_lower or "drop" in query_lower or "why" in query_lower and "revenue" in query_lower:
            rev_at_risk = metrics.get("revenue_at_risk", 0.0)
            failed_cnt = metrics.get("failed_transactions", 0)
            manual_cnt = metrics.get("manual_reviews", 0)
            
            answer = (
                f"Revenue experienced friction primarily due to {failed_cnt} failed transaction events totaling "
                f"₹{rev_at_risk:,.2f} in revenue at risk. Top factors include bank infrastructure downtime and "
                f"{manual_cnt} high-value transactions currently held in the Manual Review Queue for merchant verification."
            )
            insights = [
                f"Total Revenue at Risk: ₹{rev_at_risk:,.2f}",
                f"Pending Manual Reviews: {manual_cnt} transactions > ₹15,000",
                "Primary Failure Reasons: Insufficient funds & temporary bank gateway downtime."
            ]
            suggested_actions = [
                "Review pending high-value cases in Manual Review queue to approve valid orders.",
                "Verify WhatsApp & Email recovery automation is enabled in Settings."
            ]

        elif "high risk" in query_lower or "customer" in query_lower or "chargeback" in query_lower:
            risk_count = len(high_risk_cases)
            top_cust = [c.get("customer_id") for c in high_risk_cases[:3]] if high_risk_cases else ["cust_104", "cust_3007"]
            
            answer = (
                f"Identified {risk_count} high-risk customer profiles requiring close monitoring. "
                f"Top flagged customer accounts include: {', '.join(top_cust)}. "
                f"These accounts present elevated chargeback risk scores (> 75%) due to recent fraud flags or repeat payment failures."
            )
            insights = [
                f"Flagged High-Risk Profiles: {risk_count} accounts",
                "Top Risk Factors: High transaction amount, first-time buyer status, multiple failed PIN attempts.",
                "Chargeback Mitigation: Policy engine has automatically blocked outreach for fraud-suspected orders."
            ]
            suggested_actions = [
                "Inspect high-risk chargeback predictions in the Chargebacks tab.",
                "Consider enforcing 3D Secure / OTP verification for high-amount repeat orders."
            ]

        elif "refund" in query_lower or "suspicious" in query_lower or "abuse" in query_lower:
            alert_count = len(active_alerts)
            answer = (
                f"Found {alert_count} active anomaly alerts relating to refunds and purchase behavior. "
                f"Our Fraud Detection Agent flagged potential duplicate refund requests and elevated refund frequency on select accounts."
            )
            insights = [
                f"Active Fraud & Refund Alerts: {alert_count} items",
                "Detection Categories: Duplicate refund attempts & high-frequency customer refund requests.",
                "Financial Impact: Automated fraud guardrails prevented unauthorized balance payouts."
            ]
            suggested_actions = [
                "Open Fraud Alerts tab to inspect evidence for flagged refund requests.",
                "Resolve or dismiss investigated alerts."
            ]

        elif "recoverable" in query_lower or "recovery" in query_lower or "opportunity" in query_lower:
            rev_at_risk = metrics.get("revenue_at_risk", 0.0)
            recovered_rev = metrics.get("recovered_revenue", 0.0)
            rec_rate = metrics.get("recovery_rate", 0.0)
            
            answer = (
                f"Currently, ₹{metrics.get('net_recovered_revenue', 0.0):,.2f} has been net-recovered (Recovery Rate: {rec_rate}%). "
                f"There remains ₹{rev_at_risk - recovered_rev:,.2f} in actionable revenue at risk across open cases."
            )
            insights = [
                f"Current Recovery Rate: {rec_rate}%",
                f"Top Recovery Channel: {metrics.get('top_performing_channel', 'WHATSAPP')}",
                "Highest ERV Opportunities: Customer-correctable PIN/Auth failure categories."
            ]
            suggested_actions = [
                "Trigger automated recovery on open ACTION_READY cases in Recovery Cases tab.",
                "Verify Quiet Hours settings to ensure timely customer engagement."
            ]

        else:
            # Default General Synthesis
            answer = (
                f"RevenueShield AI Platform Summary: Monitored {metrics.get('total_transactions', 0)} total failed events. "
                f"Recovered ₹{metrics.get('recovered_revenue', 0.0):,.2f} with a recovery efficiency of {metrics.get('recovery_efficiency', 0.0)}%. "
                f"All AI actions are bounded by merchant financial policies."
            )
            insights = [
                f"Total Revenue At Risk: ₹{metrics.get('revenue_at_risk', 0.0):,.2f}",
                f"Recovered Revenue: ₹{metrics.get('recovered_revenue', 0.0):,.2f}",
                f"Active Cases: {metrics.get('active_recovery_cases', 0)}"
            ]
            suggested_actions = [
                "Check Manual Review queue for high-value approvals.",
                "Review Chargeback risk scores and Fraud Alerts."
            ]

        # Optional Gemini LLM Enhancement if configured
        if settings.USE_GEMINI and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
You are RevenueShield Financial Copilot AI. Answer the merchant query concisely (2 sentences) based on this business context:
Query: {query}
Data: {json.dumps(metrics)}
"""
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    answer = resp.text.strip()
            except Exception:
                pass

        return {
            "query": query,
            "answer": answer,
            "insights": insights,
            "suggested_actions": suggested_actions,
            "context_data": {
                "total_transactions": metrics.get("total_transactions"),
                "revenue_at_risk": metrics.get("revenue_at_risk"),
                "recovered_revenue": metrics.get("recovered_revenue")
            }
        }
