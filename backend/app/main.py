import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, SessionLocal
from app.api import health, cases, recovery, analytics, audit, settings as settings_api, webhooks
from app.services.recovery_service import RecoveryService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    init_db()
    
    # Auto-seed database if empty
    db = SessionLocal()
    try:
        from app.models.recovery_case_model import RecoveryCaseModel
        cnt = db.query(RecoveryCaseModel).count()
        if cnt == 0:
            print("[INFO] Empty database detected. Seeding initial payment failure cases...")
            from app.api.webhooks import seed_demo_data
            seed_demo_data(db)
    except Exception as e:
        print(f"[WARNING] Auto-seed failed on startup: {e}")
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI-powered revenue recovery system for failed payments (Razorpay AI Buildathon)",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local React dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to RevenueShield AI API Server",
        "tagline": "Detect. Decide. Recover. Measure.",
        "buildathon": "Razorpay AI Buildathon (Track 3 — AI Revenue Recovery)",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "cases_url": "/api/cases",
        "analytics_url": "/api/analytics"
    }

# Mount API Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(cases.router, prefix="/api", tags=["Cases"])
app.include_router(recovery.router, prefix="/api", tags=["Recovery Actions"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(audit.router, prefix="/api", tags=["Audit Trail"])
app.include_router(settings_api.router, prefix="/api", tags=["Settings"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks & Demo"])

# Mock Checkout Payment Portal Page Endpoint
@app.get("/demo/pay/{case_id}", response_class=HTMLResponse)
def demo_checkout_page(case_id: str):
    db = SessionLocal()
    try:
        from app.models.recovery_case_model import RecoveryCaseModel
        case = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.id == case_id).first()
        if not case:
            return HTMLResponse(content="<h1>Case not found</h1>", status_code=404)

        amount_fmt = f"₹{case.amount:,.2f}"
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Razorpay Demo Checkout - RevenueShield AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }}
                .checkout-container {{ background: #131c2e; border: 1px solid #1e293b; border-radius: 16px; width: 100%; max-width: 440px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #1e293b, #0f172a); padding: 24px; border-bottom: 1px solid #1e293b; text-align: center; position: relative; }}
                .demo-tag {{ position: absolute; top: 12px; right: 12px; background: #3b82f6; color: white; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px; }}
                .merchant-title {{ font-size: 14px; color: #94a3b8; margin: 0; }}
                .amount-display {{ font-size: 32px; font-weight: 800; color: #38bdf8; margin: 8px 0 0 0; }}
                .details-box {{ padding: 24px; }}
                .detail-row {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 12px; color: #94a3b8; }}
                .detail-row span:last-child {{ color: #e2e8f0; font-weight: 600; }}
                .method-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin: 16px 0; display: flex; align-items: center; justify-content: space-between; }}
                .btn-success {{ width: 100%; background: #10b981; color: white; border: none; padding: 14px; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; margin-bottom: 12px; transition: background 0.2s; }}
                .btn-success:hover {{ background: #059669; }}
                .btn-fail {{ width: 100%; background: #ef4444; color: white; border: none; padding: 12px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; opacity: 0.8; transition: opacity 0.2s; }}
                .btn-fail:hover {{ opacity: 1; }}
                .footer-note {{ text-align: center; font-size: 11px; color: #64748b; margin-top: 16px; }}
            </style>
        </head>
        <body>
            <div class="checkout-container">
                <div class="header">
                    <span class="demo-tag">DEMO PAYMENT</span>
                    <p class="merchant-title">RevenueShield Merchant Checkout</p>
                    <div class="amount-display">{amount_fmt}</div>
                </div>
                <div class="details-box">
                    <div class="detail-row">
                        <span>Invoice Reference</span>
                        <span>inv_{case.id}</span>
                    </div>
                    <div class="detail-row">
                        <span>Customer ID</span>
                        <span>{case.customer_id}</span>
                    </div>
                    <div class="detail-row">
                        <span>Failure Reason</span>
                        <span style="color: #f87171;">{case.failure_reason}</span>
                    </div>
                    <div class="method-box">
                        <span style="font-size: 13px; color: #cbd5e1;">Payment Method</span>
                        <span style="font-size: 13px; font-weight: 700; color: #38bdf8;">UPI / Razorpay Test Mode</span>
                    </div>
                    <form action="/api/demo/cases/{case.id}/payment-success" method="POST">
                        <button type="submit" class="btn-success">SIMULATE SUCCESS (PAY NOW)</button>
                    </form>
                    <button type="button" onclick="alert('Payment simulation cancelled/failed.')" class="btn-fail">SIMULATE FAILURE</button>
                    <div class="footer-note">RevenueShield AI Payment Recovery Gateway Simulator</div>
                </div>
            </div>
        </body>
        </html>
        """)
    finally:
        db.close()
