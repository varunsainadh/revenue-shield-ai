# RevenueShield AI — ML Model Evaluation Report

**Trained At:** `2026-09-02T18:08:25.378029`  
**Dataset Size:** 1000 synthetic records  
**Random Seed:** 42  
**Train/Test Split:** 80% / 20% Stratified  

> [!NOTE]
> **Dataset Assumption & Disclaimer:**  
> This evaluation was performed on a synthetic payment failure recovery dataset generated specifically for the Razorpay AI Buildathon. Metrics reflect model capacity to learn probabilistic recovery patterns on simulated data and are not claims of live production performance.

---

## Performance Summary Table

| Recovery Channel | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 0.6000 | 0.5968 | 0.7115 | 0.6491 | 0.6141 |
| **WHATSAPP** | 0.8050 | 0.8046 | 0.9655 | 0.8777 | 0.7740 |
| **VOICE** | 0.6550 | 0.6237 | 0.6304 | 0.6270 | 0.7347 |

---

## Confusion Matrices

### EMAIL Channel Model
- **True Negatives (TN):** 46
- **False Positives (FP):** 50
- **False Negatives (FN):** 30
- **True Positives (TP):** 74

### WHATSAPP Channel Model
- **True Negatives (TN):** 21
- **False Positives (FP):** 34
- **False Negatives (FN):** 5
- **True Positives (TP):** 140

### VOICE Channel Model
- **True Negatives (TN):** 73
- **False Positives (FP):** 35
- **False Negatives (FN):** 34
- **True Positives (TP):** 58

