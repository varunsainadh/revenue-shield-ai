# RevenueShield AI — 5-Minute Video Demo Script

> **Buildathon:** Razorpay AI Buildathon — **Track 3: AI Revenue Recovery**  
> **Tagline:** *"Detect. Decide. Recover. Measure."*

---

## Timeline & Presentation Script

### 0:00–0:30 | The Problem
> **Visual:** Screen opens on RevenueShield AI Dashboard showing `Revenue At Risk: ₹3,538,366.28`.
>
> **Voiceover:**  
> "Every month, thousands of digital transactions fail due to simple issues like incorrect PINs, temporary bank downtime, or low account balances. Most merchants treat all payment failures the same — sending generic retry emails or ignoring them altogether. This leads to customer drop-off, wasted outreach costs, and millions in lost revenue at risk."

---

### 0:30–1:00 | The Solution
> **Visual:** Highlight top metrics cards: `Recovered Revenue`, `Recovery Rate: 6.76%`, and `Active Recovery Cases`.
>
> **Voiceover:**  
> "Introducing **RevenueShield AI** — an autonomous revenue recovery engine built for Razorpay merchants. RevenueShield detects payment failures in real time, classifies root cause failure categories, scores channel recovery probabilities using ML models, enforces financial guardrails, creates Razorpay Test Mode payment links, and measures net recovered revenue."

---

### 1:00–1:40 | Architecture & Principles
> **Visual:** Switch to Architecture Diagram / `architecture.md` showing AI recommends $\rightarrow$ Policy validates $\rightarrow$ System executes $\rightarrow$ Human approves.
>
> **Voiceover:**  
> "Our architecture follows a strict fintech safety principle: **AI recommends, Policy validates, System executes, Human approves sensitive actions.** We never allow an LLM or ML model to directly execute unrestricted financial transactions without policy validation."

---

### 1:40–3:20 | Live Recovery Demo (Scenarios 1, 2 & 3)

#### Demo Scenario 1: Standard AI Recovery (₹2,499)
> **Visual:** Click on Case `rc_demo_1` (Amount: ₹2,499, Failure: `incorrect_pin`). Click **"Run RevenueShield Agent"**.
>
> **Voiceover:**  
> "Let's run a recovery demo. Here is a ₹2,499 failed payment caused by an incorrect PIN. The agent runs our scikit-learn model, predicting an 82% WhatsApp recovery probability and calculating an Expected Recovery Value (ERV) of ₹2,049. The policy engine approves the action, creates a Razorpay payment link, and sends the intervention."
>
> **Visual:** Click **"Open Demo Checkout Page"** $\rightarrow$ Click **"SIMULATE SUCCESS"**. Switch back to dashboard $\rightarrow$ Case transitions to `RECOVERED` and `Recovered Revenue` increases by ₹2,499.

#### Demo Scenario 2: High-Value Manual Approval Guardrail (₹18,999)
> **Visual:** Click on Case `rc_demo_3` (Amount: ₹18,999, Failure: `authentication_failed`). Click **"Run RevenueShield Agent"**.
>
> **Voiceover:**  
> "Now let's examine a high-value ₹18,999 transaction. The ML model recommends WhatsApp, but our `HighValueApprovalPolicy` intercepts it because the amount exceeds our merchant auto-approval threshold of ₹15,000. It enters the **Manual Review Queue**. As a merchant operator, I review the audit details and click **APPROVE & RECOVER**."

#### Demo Scenario 3: Fraud Risk Block (₹4,999)
> **Visual:** Click on Case `rc_demo_4` (Failure: `fraud_suspected`, Risk: `HIGH`). Click **"Run RevenueShield Agent"**.
>
> **Voiceover:**  
> "Finally, here is a suspicious transaction flagged as `fraud_suspected`. Our `FraudRiskPolicy` immediately blocks outreach, changing the status to `STOPPED` with a `DO_NOT_RETRY` directive. This prevents offensive retries on fraudulent attempts."

---

### 3:20–4:00 | AI & Expected Recovery Value (ERV)
> **Visual:** Open Case Details modal showing ERV comparison card (EMAIL vs WHATSAPP vs VOICE).
>
> **Voiceover:**  
> "Our scoring engine calculates channel recovery probabilities using trained scikit-learn classifiers (`GradientBoostingClassifier`). Expected Recovery Value (ERV) is calculated as $P(\text{recovery}) \times \text{Amount}$ minus simulated channel costs (Email = ₹2, WhatsApp = ₹5, Voice = ₹15). RevenueShield always selects the channel yielding the highest Net ERV."

---

### 4:00–4:30 | Policy Guardrails & Compliance
> **Visual:** Navigate to **Settings** page showing High-Value Threshold, Maximum Attempts, and Quiet Hours.
>
> **Voiceover:**  
> "Merchants retain full control. Through our Settings interface, merchants configure auto-approval amounts, maximum retry limits (default: 3 attempts), and Quiet Hours rules that block voice calls between 21:00 and 09:00 IST."

---

### 4:30–4:50 | Audit Trail & Business Analytics
> **Visual:** Navigate to **Audit Trail** and **Analytics** pages.
>
> **Voiceover:**  
> "Every decision, ML score, policy check, and webhook event is recorded in an immutable audit trail. Our Analytics dashboard provides real-time visibility into recovery rates, channel yields, and net recovered revenue."

---

### 4:50–5:00 | Closing
> **Visual:** Overview Dashboard showing recovered revenue metrics.
>
> **Voiceover:**  
> "**RevenueShield AI** transforms lost revenue into recovered growth — safely, intelligently, and autonomously. Thank you!"
