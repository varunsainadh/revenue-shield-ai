import os
from typing import Dict, Any, Optional
from app.config import settings

class LLMReasoner:
    @staticmethod
    def generate_explanation(
        case_data: Dict[str, Any],
        recommendation: Dict[str, Any],
        fallback_reason: str
    ) -> str:
        if not settings.USE_GEMINI or not settings.GEMINI_API_KEY:
            return fallback_reason

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
You are a senior fintech recovery AI assistant. Provide a single concise, professional sentence summarizing why this recovery channel and strategy was chosen for the merchant dashboard. Do not expose internal chain-of-thought.

Case Details:
- Amount: ₹{case_data.get('amount')}
- Failure Reason: {case_data.get('failure_reason')}
- Recommended Channel: {recommendation.get('recommended_channel')}
- Recommended Action: {recommendation.get('recommended_action')}
- Highest ERV: ₹{recommendation.get('channel_scores', {}).get(recommendation.get('recommended_channel', '').lower(), {}).get('erv', 0.0)}

Return ONLY the single concise explanation sentence.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            # Fallback gracefully
            pass

        return fallback_reason
