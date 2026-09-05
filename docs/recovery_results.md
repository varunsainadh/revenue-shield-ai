# RevenueShield AI — 500-Case Batch Recovery Benchmark Results

**Razorpay AI Buildathon — Track 3: AI Revenue Recovery**  
**Execution Timestamp:** 2026-09-05 03:56:10 UTC  
**Batch Size:** 500 simulated payment failure events

---

## 1. Headline Recovery Performance

| Metric | Measured Result |
| :--- | :--- |
| **Total Revenue At Risk** | **₹3,750,100.00** |
| **Total Recovered Revenue** | **₹848,952.00** |
| **Recovery Yield Rate (₹)** | **22.64%** |
| **Case Recovery Conversion (%)** | **49.60%** (248 of 500 cases) |
| **Average Time-to-Recovery** | **42 seconds** (Autonomous webhook processing) |

---

## 2. Channel Performance Breakdown

| Channel | Successful Recoveries | Total Recovered Amount (₹) | Share of Recovery |
| :--- | :---: | :---: | :---: |
| **WhatsApp** | 171 | ₹699,029.00 | 82.3% |
| **Email** | 77 | ₹149,923.00 | 17.7% |
| **Voice Call** | 0 | ₹0.00 | 0.0% |

---

## 3. Governance & Policy Resolution Breakdown

| Decision Category | Case Count | Policy / Guardrail Applied |
| :--- | :---: | :--- |
| **Auto-Resolved & Recovered** | **248** | Approved by `QuietHoursPolicy`, `MaximumAttemptsPolicy`, `FraudRiskPolicy` |
| **Escalated to Manual Review** | **115** | Intercepted by `HighValueApprovalPolicy` (Amount threshold) |
| **Blocked & Stopped** | **38** | Blocked by `FraudRiskPolicy` (Risk level HIGH/CRITICAL or `fraud_suspected`) |
| **Failed / Expired** | **99** | Customer window elapsed without payment completion |

---

## 4. Failure Reason Recovery Breakdown

```
Failure Reason           Recovered Amount (₹)
--------------------------------------------------
incorrect_pin            ₹382,079.00
authentication_failed    ₹254,235.00
insufficient_funds       ₹81,178.00
bank_down                ₹76,576.00
customer_cancelled       ₹54,884.00
```
