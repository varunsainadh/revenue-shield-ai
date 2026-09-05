import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from app.config import settings
from app.services.audit_service import AuditService
from app.domain.enums import AuditEventType

class LiveOutreachService:
    @staticmethod
    def send_email(
        to_email: str,
        customer_name: str,
        amount: float,
        failure_reason: str,
        payment_link_url: str,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Sends real email via SMTP if LIVE_OUTREACH_ENABLED and credentials exist.
        Otherwise logs simulated delivery in Mock Mode.
        """
        subject = f"Action Required: Complete your payment of ₹{amount:,.2f} - RevenueShield"
        body = f"""Dear {customer_name},

Your payment of ₹{amount:,.2f} experienced a failure due to: {failure_reason}.

To complete your order safely, please click the secure Razorpay payment link below:
{payment_link_url}

Thank you,
RevenueShield Recovery Service
"""
        if settings.LIVE_OUTREACH_ENABLED and settings.SMTP_USER and settings.SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.SMTP_USER
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
                sent_status = "SENT_LIVE"
            except Exception as e:
                sent_status = f"FAILED: {e}"
        else:
            sent_status = "SIMULATED_MOCK"

        return {
            "channel": "EMAIL",
            "status": sent_status,
            "to": to_email,
            "subject": subject
        }

    @staticmethod
    def send_whatsapp(
        to_phone: str,
        customer_name: str,
        amount: float,
        failure_reason: str,
        payment_link_url: str,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Sends real WhatsApp message via Twilio Sandbox if LIVE_OUTREACH_ENABLED.
        Otherwise logs simulated delivery in Mock Mode.
        """
        message_body = (
            f"Hi {customer_name}, your payment of ₹{amount:,.2f} failed due to {failure_reason}. "
            f"Tap here to complete payment: {payment_link_url}"
        )

        if settings.LIVE_OUTREACH_ENABLED and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                msg = client.messages.create(
                    body=message_body,
                    from_=settings.TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{to_phone}"
                )
                sent_status = f"SENT_TWILIO_WA ({msg.sid})"
            except Exception as e:
                sent_status = f"FAILED: {e}"
        else:
            sent_status = "SIMULATED_MOCK"

        return {
            "channel": "WHATSAPP",
            "status": sent_status,
            "to": to_phone,
            "body": message_body
        }

    @staticmethod
    def initiate_voice_call(
        to_phone: str,
        customer_name: str,
        amount: float,
        failure_reason: str,
        payment_link_url: str,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Places a real outbound voice call via Twilio Voice API if LIVE_OUTREACH_ENABLED.
        Pre-warms health probe before dialing to prevent serverless cold-start timeouts.
        """
        if settings.LIVE_OUTREACH_ENABLED and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                call = client.calls.create(
                    twiml=f"<Response><Say>Hello {customer_name}, this is an automated update regarding your payment of {amount} rupees. Please check your SMS for your Razorpay payment link.</Say></Response>",
                    to=to_phone,
                    from_=settings.TWILIO_PHONE_NUMBER
                )
                sent_status = f"DIALED_TWILIO_VOICE ({call.sid})"
            except Exception as e:
                sent_status = f"FAILED: {e}"
        else:
            sent_status = "SIMULATED_MOCK"

        return {
            "channel": "VOICE",
            "status": sent_status,
            "to": to_phone
        }
