# RevenueShield AI — Autonomous AI Revenue Recovery Platform

> **Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**  
> *"Detect. Decide. Recover. Measure."*

[![Razorpay AI Buildathon](https://img.shields.io/badge/Razorpay%20AI%20Buildathon-Track%2003%20%E2%80%94%20AI%20Revenue%20Recovery-blue.svg)](https://razorpay.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🏆 Track 03 Benchmark Batch Recovery Results

> **Scope Clarification:** Built specifically for **Track 03 (AI Revenue Recovery)**. Supporting capabilities like Chargeback Risk Prediction and Fraud Anomaly Detection are included strictly as **risk signals that inform recovery channel selection and stopping rules**, not as standalone parallel features.

```
===================================================================================
                REVENUESHIELD 500-CASE RECOVERY BENCHMARK RESULTS
===================================================================================
  Total Revenue At Risk:               ₹3,750,100.00
  Total Revenue Recovered:             ₹2,558,400.00
  Actionable Recovery Yield Rate:      68.22% (on customer-correctable failures)
  Average Time-to-Recovery:            42 seconds (autonomous webhook processing)
  Escalated to Manual Review:          61 cases (high-value threshold >= ₹15,000)
  Blocked by Risk Guardrails:          18 cases (fraud / high risk flagged)
===================================================================================
```

---

## ⚖️ Judging Bar Alignment (Track 03 Criteria)

RevenueShield AI is architected directly against the official Razorpay AI Buildathon Track 03 judging bar:

1. **Stopping Rules (`MaximumAttemptsPolicy`):**
   Explicitly caps recovery outreach at a maximum of **3 attempts per case**. Once reached, the case transitions to `STOPPED` with a `DO_NOT_RETRY` directive to eliminate customer spam and infinite retry loops.

2. **Compliant Escalation (`QuietHoursPolicy` & `HighValueApprovalPolicy`):**
   - **`QuietHoursPolicy`:** Enforces telecom compliance by suppressing voice call outreach during quiet hours (**21:00 to 09:00 IST**).
   - **`HighValueApprovalPolicy`:** Intercepts high-value transactions ($\ge$ **₹15,000**) and escalates them to the **Merchant Manual Review Queue** for human sign-off before payment links are dispatched.

3. **Visible End-to-End Audit Trail ([Audit Log Viewer](file:///backend/app/models/audit_model.py)):**
   Every decision, ML scoring event, policy evaluation, and Razorpay webhook state transition is stored in an immutable `AuditLog` table and rendered visually in the operations dashboard.

---

## 🧠 AI Judgment: AI Recommends. Policy Validates. System Executes. Human Approves.

RevenueShield AI applies AI where probabilistic reasoning excels (ML channel scoring, Expected Recovery Value estimation, Hinglish voice intent parsing) while enforcing **100% deterministic logic for financial guardrails**:

### Why Guardrails are Kept Deterministic:
- **Quiet Hours Calculation:** Uses exact datetime window logic rather than LLM prompts. *Why? LLMs can hallucinate time zones or miscalculate 21:00-09:00 IST boundaries.*
- **High-Value Escalation:** Uses strict float comparison (`amount >= 15000.0`). *Why? Financial compliance thresholds require guaranteed, deterministic execution without probabilistic variance.*

---

## 🛠️ "What Broke, and How We Recovered" (Engineering Post-Mortem)

During development and stress-testing, we encountered and solved three real-world engineering failures:

### 1. Razorpay Test-Mode 30-Active-Link Cap (`HTTP 429` Under Load)
- **The Failure:** When running high-volume batch recoveries, Razorpay's Test Mode API returned `HTTP 429 Too Many Requests` due to a strict cap of 30 concurrently active payment links per key.
- **The Solution:** Implemented an adaptive payment link gateway pool ([`PaymentLinkService`](file:///backend/app/services/payment_link_service.py)) that caches and reconciles unexpired links matching invoice amounts instead of constantly minting new ones.

### 2. Twilio Cold-Start Webhook Timeout (15-Second Limit)
- **The Failure:** Serverless scale-to-zero hosting caused TwiML webhook responses to exceed Twilio's 15-second timeout on cold starts, resulting in dropped voice recovery calls.
- **The Solution:** Built an automated pre-warming health probe ([`/api/health`](file:///backend/app/api/health.py)) that sends heartbeat pings to keep the backend warm prior to executing voice outreach.

### 3. SQLite Concurrency Locking Under Batch Pipeline Load
- **The Failure:** Multi-threaded batch ingestion caused `sqlite3.OperationalError: database is locked` during concurrent audit log writes.
- **The Solution:** Enabled Write-Ahead Logging (`WAL` mode) and implemented exponential backoff retry logic in database session management.

---

## 🇮🇳 Hinglish Code-Switching Voice Recovery (Twilio Agent Integration)

Designed specifically for Indian digital commerce, the voice recovery engine ([`parse_hinglish_voice_intent`](file:///backend/app/agents/deterministic_reasoner.py)) parses spoken Hinglish code-switching responses:

- *"Friday ko pay kar dunga"* $\rightarrow$ Schedules a **Promise-to-Pay (PTP)** for Friday.
- *"Kal payment clear kar dunga"* $\rightarrow$ Schedules a **Promise-to-Pay (PTP)** for Tomorrow.
- *"Passcode issue ho gaya thha"* $\rightarrow$ Classifies failure as `incorrect_pin`.
- *"Bank server down chal raha hai"* $\rightarrow$ Classifies failure as `bank_down`.

---

## 📊 Honest Machine Learning Metrics & Evaluation

Trained on 1,000 synthetic payment failure records using scikit-learn (`GradientBoostingClassifier` with `ColumnTransformer` preprocessing):

| Model Channel | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Top Feature Drivers |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **WhatsApp Model** | **80.5%** | **80.5%** | **96.6%** | **87.8%** | **0.774** | Device Type (Mobile), Failure Reason |
| **Voice Model** | **65.5%** | **62.4%** | **63.0%** | **62.7%** | **0.735** | Historical Success Rate, Amount |
| **Email Model** | **60.0%** | **59.7%** | **71.2%** | **64.9%** | **0.614** | Failure Category, Hour of Day |

> **Limitations Note:** Models were trained on synthetic transaction datasets generated with seed 42 to simulate Indian merchant payment failure distributions (`incorrect_pin`, `bank_down`, `insufficient_funds`).

---

## 📐 System Architecture

```mermaid
graph TD
    SubGraph1[Payment Failure Event] -->|Webhook / API| API[FastAPI Ingestion Endpoint]
    API --> Service[RecoveryService Layer]
    Service --> DB[(SQLite / PostgreSQL DB)]

    subgraph Multi-Agent Shared Workflow
        Service --> SharedWorkflow[Multi-Agent Orchestrator]
        SharedWorkflow --> FraudAgent[1. Fraud Risk Agent]
        SharedWorkflow --> ChargebackAgent[2. Chargeback XAI Agent]
        SharedWorkflow --> RecoveryAgent[3. Revenue Recovery Agent]
        SharedWorkflow --> CopilotAgent[4. Financial Copilot Agent]
    end

    subgraph ML & Expected Recovery Value (ERV) Engine
        RecoveryAgent --> MLPredictor[scikit-learn Predictor]
        MLPredictor --> ERV[Net ERV Engine: Prob x Amount - Cost]
    end

    subgraph Policy Engine & Guardrails
        ERV --> Policy[Deterministic Policy Engine]
        Policy -->|High Value >= 15k| Manual[HighValueApprovalPolicy -> Manual Review]
        Policy -->|Fraud Flag / Max Attempts| Block[MaximumAttemptsPolicy / FraudPolicy -> Block]
        Policy -->|Quiet Hours 21:00-09:00| Quiet[QuietHoursPolicy -> Suppress Voice]
        Policy -->|Approved| Exec[Razorpay Test Mode / Mock Payment Link]
    end

    subgraph Operations Dashboard
        Exec --> UI[React Dashboard & Visible Audit Trail]
        Manual --> UI
        CopilotAgent --> UI
    end
```

---

## 🚀 Quickstart & Setup Guide

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- **API Documentation:** `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- **Operations Dashboard:** `http://localhost:3000`

### 3. Run Recovery Batch & Test Suite
```bash
# Execute 500-case recovery batch simulation
python scripts/run_recovery_batch.py

# Run full automated Pytest test suite (19/19 tests passing)
cd backend && pytest
```

---

## 📝 Submission Checklist

- [x] README leads with quantified 500-case batch recovery results
- [x] Visible Audit Trail implemented & documented
- [x] Stopping rules (`MaximumAttemptsPolicy`) and escalation (`QuietHoursPolicy`, `HighValueApprovalPolicy`) named explicitly
- [x] Dedicated "What Broke, and How We Recovered" engineering post-mortem section
- [x] Feature narrative centered on Track 03 (AI Revenue Recovery)
- [x] Real ML metrics (Accuracy, Precision, Recall, ROC-AUC) pasted into README
- [x] Hinglish code-switching voice recovery parser implemented
- [x] All 19 Pytest tests passing 100% clean
- [x] Architecture documentation (`architecture.md`) updated

---

## 📜 License

Distributed under the **MIT License**.
