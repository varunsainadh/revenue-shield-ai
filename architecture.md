# RevenueShield AI — System Architecture & Design Specification

"Detect. Decide. Recover. Measure."  
**Razorpay AI Buildathon — Track 3 — AI Revenue Recovery**

---

## 1. High-Level System Architecture

```mermaid
graph TD
    SubGraph1[Payment Event Sources] -->|Webhook / API| API[FastAPI Ingestion Endpoint]
    API --> Service[RecoveryService Layer]
    Service --> DB[(SQLite / PostgreSQL DB)]

    subgraph AI & Scoring Engine
        Service --> ML[MLPredictor Engine]
        ML --> FeatureEng[Feature Engineering Pipeline]
        ML --> Models[scikit-learn Models: Email / WA / Voice]
        Models --> ERV[ERV Engine: Prob x Amount - Cost]
    end

    subgraph Decisioning & Policy Guardrails
        ERV --> Agent[RecoveryAgent Reasoner]
        Agent --> Policy[Policy Engine Guardrails]
        Policy -->|High Value >= 15k| Manual[Manual Review Queue]
        Policy -->|Fraud Flag / Max Attempts| Block[Block & Stop Automation]
        Policy -->|Approved| Exec[Execute Recovery]
    end

    subgraph Execution & Razorpay Integration
        Exec --> RzpAdapter[Razorpay Test Mode Adapter]
        RzpAdapter --> PaymentLink[Razorpay Payment Link / Mock Checkout]
        PaymentLink --> Customer[Customer Completes Payment]
        Customer --> Webhook[Razorpay Webhook Handler]
        Webhook -->|Signature Verified| Complete[State -> RECOVERED]
        Complete --> Metrics[Update Recovered Revenue & Audit Trail]
    end
```

---

## 2. Recovery Case State Machine

```mermaid
stateDiagram-v2
    [*] --> OPEN
    OPEN --> ANALYZING : Agent analysis triggered
    ANALYZING --> ACTION_READY : ERV high & policy approved
    ANALYZING --> MANUAL_REVIEW : Amount >= ₹15,000 threshold
    ANALYZING --> STOPPED : Fraud flag or risk decline
    
    MANUAL_REVIEW --> ACTION_READY : Merchant operator approves
    MANUAL_REVIEW --> STOPPED : Merchant operator rejects
    
    ACTION_READY --> PENDING_RECOVERY : Recovery action initiated
    PENDING_RECOVERY --> WAITING_PAYMENT : Payment link created & sent
    WAITING_PAYMENT --> RECOVERED : Razorpay webhook confirms payment
    WAITING_PAYMENT --> FAILED : Max attempts or window exceeded
    
    RECOVERED --> [*]
    STOPPED --> [*]
    FAILED --> [*]
```

---

## 3. Promise-to-Pay (PTP) State Machine

```mermaid
stateDiagram-v2
    [*] --> ACTIVE : Customer schedules future date
    ACTIVE --> KEPT : Payment completed on or before date
    ACTIVE --> BROKEN : Date passed without payment
    ACTIVE --> EXPIRED : Recovery window elapsed
    
    KEPT --> [*]
    BROKEN --> [*]
    EXPIRED --> [*]
```

---

## 4. Policy Engine Flowchart

```mermaid
flowchart TD
    Start[Proposed Recovery Action] --> P1{Already Recovered?}
    P1 -- Yes --> Block1[BLOCK: Case already recovered]
    P1 -- No --> P2{Fraud or Severe Risk?}
    P2 -- Yes --> Block2[BLOCK: Risk / Fraud suspected]
    P2 -- No --> P3{Attempts >= Max Attempts?}
    P3 -- Yes --> Block3[BLOCK: Max attempts reached]
    P3 -- No --> P4{Amount >= ₹15,000?}
    P4 -- Yes --> Manual[MANUAL_REVIEW: High value threshold]
    P4 -- No --> P5{Active Promise-to-Pay?}
    P5 -- Yes --> Delay1[DELAY: Active PTP scheduled]
    P5 -- No --> P6{Quiet Hours 21:00-09:00?}
    P6 -- Yes & Voice --> Block4[BLOCK: Voice calls muted in quiet hours]
    P6 -- No --> Approve[ALLOW: Action Approved for Execution]
```

---

## 5. Razorpay Webhook Signature & Idempotency Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Rzp as Razorpay Gateway / Mock Portal
    participant API as FastAPI /api/webhooks/razorpay
    participant Service as RecoveryService
    participant DB as Database & Audit Log

    Customer->>Rzp: Completes Payment via Link
    Rzp->>API: POST /api/webhooks/razorpay (Payload + X-Razorpay-Signature)
    API->>API: Verify Signature (HMAC SHA256)
    alt Signature Invalid
        API-->>Rzp: HTTP 400 (Invalid Signature) & Log WEBHOOK_REJECTED
    else Signature Valid
        API->>Service: process_payment_success(case_id)
        alt Case Already RECOVERED
            Service-->>API: Idempotent return (No duplicate outcome)
        else Case Active
            Service->>DB: Update State to RECOVERED & Insert RecoveryOutcome
            Service->>DB: Log REVENUE_RECOVERED Audit Event
            API-->>Rzp: HTTP 200 (Processed)
        end
    end
```

---

## 6. Database Entity-Relationship Diagram

```mermaid
erDiagram
    RECOVERY_CASES ||--o{ PROMISES_TO_PAY : "has"
    RECOVERY_CASES ||--o{ RECOVERY_OUTCOMES : "produces"
    RECOVERY_CASES ||--o{ PAYMENT_LINKS : "bound to"
    RECOVERY_CASES ||--o{ AUDIT_LOGS : "logs"

    RECOVERY_CASES {
        string id PK
        string transaction_id
        string customer_id
        float amount
        string failure_reason
        string failure_category
        string status
        float recoverability_score
        string recommended_channel
        float recommended_erv
    }

    PROMISES_TO_PAY {
        string id PK
        string recovery_case_id FK
        string customer_id
        datetime promised_date
        string status
    }

    RECOVERY_OUTCOMES {
        string id PK
        string recovery_case_id FK
        boolean recovered
        float recovered_amount
        string channel_used
    }

    PAYMENT_LINKS {
        string id PK
        string bound_case_id FK
        string invoice_reference
        float amount
        string razorpay_link_id
        string url
        string status
    }

    AUDIT_LOGS {
        string id PK
        string case_id FK
        datetime timestamp
        string event_type
        string actor
        string action
    }
```
