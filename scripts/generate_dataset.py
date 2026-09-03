import os
import random
import numpy as np
import pandas as pd

RANDOM_SEED = 42

def generate_dataset(num_records: int = 1000, seed: int = RANDOM_SEED, output_dir: str = None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    np.random.seed(seed)
    random.seed(seed)

    banks = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "PAYTM_BANK", "YES_BANK"]
    payment_methods = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET"]
    device_types = ["mobile_android", "mobile_ios", "web_desktop", "web_mobile"]
    
    failure_reasons_weights = {
        "incorrect_pin": 0.22,
        "insufficient_funds": 0.25,
        "authentication_failed": 0.15,
        "bank_down": 0.10,
        "card_expired": 0.08,
        "gateway_timeout": 0.06,
        "customer_cancelled": 0.05,
        "balance_low": 0.04,
        "fraud_suspected": 0.03,
        "risk_declined": 0.02
    }
    
    reasons_list = list(failure_reasons_weights.keys())
    probs_list = list(failure_reasons_weights.values())

    category_map = {
        "incorrect_pin": "CUSTOMER_CORRECTABLE",
        "authentication_failed": "CUSTOMER_CORRECTABLE",
        "insufficient_funds": "INSUFFICIENT_FUNDS",
        "balance_low": "INSUFFICIENT_FUNDS",
        "card_expired": "PAYMENT_METHOD_PROBLEM",
        "bank_declined": "PAYMENT_METHOD_PROBLEM",
        "bank_down": "TEMPORARY_INFRASTRUCTURE",
        "gateway_timeout": "TEMPORARY_INFRASTRUCTURE",
        "customer_cancelled": "CUSTOMER_ABANDONMENT",
        "risk_declined": "RISK_RELATED",
        "fraud_suspected": "RISK_RELATED"
    }

    records = []

    for i in range(1, num_records + 1):
        tx_id = f"pay_tx_{100000 + i}"
        cust_id = f"cust_{random.randint(1000, 9999)}"
        
        base_amt = float(np.random.lognormal(mean=7.5, sigma=1.2))
        amount = round(max(199.0, min(85000.0, base_amt)), 2)
        
        pm = random.choice(payment_methods)
        bank = random.choice(banks)
        hour = random.randint(0, 23)
        dow = random.randint(0, 6)
        
        reason = np.random.choice(reasons_list, p=probs_list)
        category = category_map[reason]
        
        prev_success = random.randint(0, 25)
        prev_fail = random.randint(0, 8)
        total_prev = prev_success + prev_fail
        success_rate = round(prev_success / total_prev, 3) if total_prev > 0 else 0.5
        
        attempt_no = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        latency = int(np.random.gamma(shape=2.0, scale=150))
        device = random.choice(device_types)
        
        if reason in ["fraud_suspected", "risk_declined"]:
            risk_level = random.choice(["HIGH", "CRITICAL"])
        elif amount > 25000:
            risk_level = random.choice(["MEDIUM", "HIGH"])
        else:
            risk_level = random.choices(["LOW", "MEDIUM", "HIGH"], weights=[0.75, 0.20, 0.05])[0]

        # Probabilistic relationships for ML training
        # 1. Base recovery likelihood from failure category
        if risk_level in ["HIGH", "CRITICAL"] or reason == "fraud_suspected":
            p_email, p_wa, p_voice = 0.02, 0.01, 0.01
        elif category == "CUSTOMER_CORRECTABLE":
            p_email = 0.55 + (success_rate * 0.25) - (attempt_no * 0.05)
            p_wa = 0.72 + (success_rate * 0.20) - (attempt_no * 0.04)
            p_voice = 0.45 + (success_rate * 0.25) - (attempt_no * 0.05)
        elif category == "INSUFFICIENT_FUNDS":
            p_email = 0.35 + (success_rate * 0.25) - (attempt_no * 0.06)
            p_wa = 0.50 + (success_rate * 0.30) - (attempt_no * 0.05)
            p_voice = 0.30 + (success_rate * 0.20) - (attempt_no * 0.05)
        elif category == "TEMPORARY_INFRASTRUCTURE":
            p_email = 0.70 - (attempt_no * 0.05)
            p_wa = 0.85 - (attempt_no * 0.04)
            p_voice = 0.55 - (attempt_no * 0.05)
        elif category == "PAYMENT_METHOD_PROBLEM":
            p_email = 0.50 + (success_rate * 0.20) - (attempt_no * 0.05)
            p_wa = 0.65 + (success_rate * 0.20) - (attempt_no * 0.05)
            p_voice = 0.40 + (success_rate * 0.20) - (attempt_no * 0.05)
        else:
            p_email, p_wa, p_voice = 0.30, 0.40, 0.25

        # 2. Channel specific nuances
        if "mobile" in device:
            p_wa += 0.08
        if "desktop" in device:
            p_email += 0.08
        if amount > 15000:
            p_voice += 0.12 # Voice performs better on high value cases

        # Clamp probabilities between 0.01 and 0.99
        p_email = max(0.01, min(0.99, p_email))
        p_wa = max(0.01, min(0.99, p_wa))
        p_voice = max(0.01, min(0.99, p_voice))

        # Sample binary labels from probability distributions
        email_success = 1 if (random.random() < p_email and risk_level not in ["HIGH", "CRITICAL"]) else 0
        wa_success = 1 if (random.random() < p_wa and risk_level not in ["HIGH", "CRITICAL"]) else 0
        voice_success = 1 if (random.random() < p_voice and risk_level not in ["HIGH", "CRITICAL"]) else 0

        recovered_flag = 1 if (email_success or wa_success or voice_success) else 0
        recovered_amt = amount if recovered_flag else 0.0

        records.append({
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "amount": amount,
            "currency": "INR",
            "payment_method": pm,
            "bank": bank,
            "hour_of_day": hour,
            "day_of_week": dow,
            "failure_reason": reason,
            "failure_category": category,
            "previous_success_count": prev_success,
            "previous_failure_count": prev_fail,
            "customer_success_rate": success_rate,
            "attempt_number": attempt_no,
            "gateway_latency_ms": latency,
            "device_type": device,
            "risk_level": risk_level,
            "email_recovery_success": email_success,
            "whatsapp_recovery_success": wa_success,
            "voice_recovery_success": voice_success,
            "recovered": recovered_flag,
            "recovered_amount": recovered_amt
        })

    df = pd.DataFrame(records)
    
    os.makedirs(output_dir, exist_ok=True)
    csv_train_path = os.path.join(output_dir, "recovery_training_data.csv")
    csv_tx_path = os.path.join(output_dir, "transactions.csv")
    
    df.to_csv(csv_train_path, index=False)
    df.to_csv(csv_tx_path, index=False)
    print(f"Generated {len(df)} reproducible synthetic records (Seed: {seed}) saved to:\n - {csv_train_path}\n - {csv_tx_path}")

if __name__ == "__main__":
    generate_dataset()
