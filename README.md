# RevenueShield AI — Autonomous AI Revenue Recovery Engine

> **Tagline:** *"Detect. Decide. Recover. Measure."*  
> **Buildathon:** Razorpay AI Buildathon — **Track 3: AI Revenue Recovery**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-blueviolet.svg)](https://razorpay.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Executive Summary

**RevenueShield AI** is an autonomous, production-ready AI revenue recovery system built for merchants using Razorpay. It ingests failed payment events, diagnoses root cause failure categories, scores channel recovery probabilities using machine learning models, calculates Expected Recovery Value (ERV), enforces strict financial and compliance policy guardrails, executes bounded recovery workflows via Razorpay Test Mode payment links, and measures net recovered revenue.

---

## Key Architectural Principle

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   AI MODELS     │  ──>  │  POLICY ENGINE  │  ──>  │ SYSTEM EXECUTES │  ──>  │ HUMAN APPROVES  │
│  (Recommends)   │       │   (Validates)   │       │  (Payment Link) │       │ (High-Value /   │
└─────────────────┘       └─────────────────┘       └─────────────────┘       │    Restricted)  │
                                                                              └─────────────────┘
```

> **Financial Safety Guarantee:** Never allow an LLM or ML model to directly execute unrestricted financial actions. All AI recommendations must be validated by deterministic financial policy guardrails before execution.

---

## Core Product Flow

```
Payment Fails (Gateway/Bank)
         │
         ▼
Failure Event Ingested & Recovery Case Created
         │
         ▼
Root Cause Failure Classification (CUSTOMER_CORRECTABLE, INSUFFICIENT_FUNDS, etc.)
         │
         ▼
Feature Extraction & ML Channel Scoring (EMAIL, WHATSAPP, VOICE)
         │
         ▼
Expected Recovery Value (ERV = Probability × Amount) Calculated
         │
         ▼
Best Recovery Strategy Proposed by RecoveryAgent
         │
         ▼
Policy Engine Validation (Quiet Hours, Max Attempts, High-Value Threshold, Risk Block)
         │
         ├───────────────────────┬───────────────────────┐
         ▼                       ▼                       ▼
   [APPROVED]             [MANUAL REVIEW]            [BLOCKED]
  Action Executed        Merchant Approves        Automation Stopped
         │                       │
         ▼                       ▼
Razorpay Payment Link Created (Test Mode or Mock Checkout Portal)
         │
         ▼
Customer Completes Payment via Link
         │
         ▼
Razorpay Webhook (payment_link.paid / payment.captured) Verified via HMAC SHA256
         │
         ▼
Recovery Case Marked RECOVERED & Analytics/Audit Logs Updated
```

---

## Key Features

### 1. Root Cause Classification
Maps raw bank/gateway error codes into actionable categories:
- `CUSTOMER_CORRECTABLE` (e.g., `incorrect_pin`, `authentication_failed`)
- `INSUFFICIENT_FUNDS` (e.g., `insufficient_funds`, `balance_low`)
- `PAYMENT_METHOD_PROBLEM` (e.g., `card_expired`, `bank_declined`)
- `TEMPORARY_INFRASTRUCTURE` (e.g., `bank_down`, `gateway_timeout`)
- `RISK_RELATED` (e.g., `fraud_suspected`, `risk_declined`)

### 2. ML Channel Scoring & ERV Engine
Uses scikit-learn classifiers (`GradientBoostingClassifier` with `ColumnTransformer` preprocessing) to estimate channel recovery probabilities:
$$\text{ERV}_{\text{channel}} = P(\text{recovery}_{\text{channel}}) \times \text{Amount}$$
$$\text{Net ERV}_{\text{channel}} = \text{ERV}_{\text{channel}} - \text{simulated\_cost}_{\text{channel}}$$

- **Simulated Intervention Costs:** Email = ₹2, WhatsApp = ₹5, Voice = ₹15.
- **Selection:** Automatically recommends the channel yielding the highest Net ERV.

### 3. Financial & Compliance Guardrail Engine
Deterministic policy checks evaluated before any execution:
- **`HighValueApprovalPolicy`:** Transactions $\ge$ ₹15,000 require manual human approval.
- **`FraudRiskPolicy`:** Risk level `HIGH`/`CRITICAL` or `fraud_suspected` immediately blocks automation.
- **`MaximumAttemptsPolicy`:** Maximum 3 recovery attempts permitted per case.
- **`QuietHoursPolicy`:** Voice outreach blocked during quiet hours (21:00 to 09:00 IST).
- **`ActivePromiseToPayPolicy`:** Outreach suppressed if customer has active PTP schedule.

### 4. Razorpay Test Mode & Built-in Mock Checkout
- Creates real Razorpay Test Mode Payment Links (`rzp_test_...`) when keys are configured.
- Provides a built-in mock checkout portal (`/demo/pay/{case_id}`) for offline demonstration without requiring external tunnels or live credentials.
- Signature verification (`X-Razorpay-Signature` HMAC SHA256) and webhook idempotency protection.

---

## Machine Learning Evaluation

Evaluated on 1,000 synthetic payment failure records generated via `scripts/generate_dataset.py` (Fixed seed: `42`):

| Channel | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 0.6000 | 0.5968 | 0.7115 | 0.6491 | 0.6141 |
| **WHATSAPP** | 0.8050 | 0.8046 | 0.9655 | 0.8777 | 0.7740 |
| **VOICE** | 0.6550 | 0.6237 | 0.6304 | 0.6270 | 0.7347 |

---

## Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Setup Backend
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run Pytest suite
pytest

# Train ML channel scoring models
python ../scripts/train_model.py

# Start FastAPI backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend Dashboard
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite React dev server
npm run dev
```
Open **`http://localhost:3000`** in your browser to interact with the dashboard.

---

## Project Structure

```
RevenueShield/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── architecture.md
├── backend/
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── model_metrics.json
│   ├── models_ml/
│   │   ├── email_recovery_model.joblib
│   │   ├── whatsapp_recovery_model.joblib
│   │   └── voice_recovery_model.joblib
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── domain/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── agents/
│       ├── ml/
│       ├── api/
│       └── tests/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── data/
│   ├── transactions.csv
│   └── recovery_training_data.csv
├── scripts/
│   ├── generate_dataset.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── run_batch_recovery.py
└── docs/
    ├── demo-script.md
    └── evaluation.md
```

---

## Demo Scenarios

Seed pre-configured test scenarios via the **"Seed Synthetic Demo Data"** button in the dashboard or API (`POST /api/demo/seed`):

1. **Scenario 1 (Standard Recovery):** ₹2,499 failure (`incorrect_pin`) $\rightarrow$ High WhatsApp ERV $\rightarrow$ Action ready $\rightarrow$ Payment link $\rightarrow$ Recovered.
2. **Scenario 2 (Infrastructure Downtime):** ₹899 failure (`bank_down`) $\rightarrow$ Wait & Retry policy delay.
3. **Scenario 3 (High-Value Transaction):** ₹18,999 failure (`authentication_failed`) $\rightarrow$ Blocked by `HighValueApprovalPolicy` $\rightarrow$ Manual review required.
4. **Scenario 4 (Fraud Flag):** ₹4,999 failure (`fraud_suspected`) $\rightarrow$ Blocked by `FraudRiskPolicy` $\rightarrow$ `DO_NOT_RETRY`.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
