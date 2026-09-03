import os
import sys
import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.scoring_service import ScoringService

def run_batch_evaluation():
    data_path = os.path.join(project_root, "data", "recovery_training_data.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at {data_path}")

    df = pd.read_csv(data_path)
    print("==================================================")
    print("REVENUESHIELD AI — BATCH ML EVALUATION & ERV SUMMARY")
    print("==================================================")
    print(f"Evaluating {len(df)} payment failure cases...\n")

    email_probs, wa_probs, voice_probs = [], [], []
    email_ervs, wa_ervs, voice_ervs = [], [], []
    recommendations = []

    for _, row in df.iterrows():
        case_dict = row.to_dict()
        res = ScoringService.get_predictions(case_dict)
        
        scores = res["channel_scores"]
        email_probs.append(scores["email"]["probability"])
        wa_probs.append(scores["whatsapp"]["probability"])
        voice_probs.append(scores["voice"]["probability"])

        email_ervs.append(scores["email"]["erv"])
        wa_ervs.append(scores["whatsapp"]["erv"])
        voice_ervs.append(scores["voice"]["erv"])

        recommendations.append(res["recommended_channel"])

    rec_counts = pd.Series(recommendations).value_counts()

    print("--- CHANNEL PROBABILITY AVERAGES ---")
    print(f"  Average Email Probability    : {np.mean(email_probs)*100:.2f}%")
    print(f"  Average WhatsApp Probability : {np.mean(wa_probs)*100:.2f}%")
    print(f"  Average Voice Probability    : {np.mean(voice_probs)*100:.2f}%\n")

    print("--- AVERAGE EXPECTED RECOVERY VALUE (ERV) ---")
    print(f"  Average Email ERV    : INR {np.mean(email_ervs):,.2f}")
    print(f"  Average WhatsApp ERV : INR {np.mean(wa_ervs):,.2f}")
    print(f"  Average Voice ERV    : INR {np.mean(voice_ervs):,.2f}\n")

    print("--- RECOMMENDED CHANNEL DISTRIBUTION ---")
    for ch, count in rec_counts.items():
        pct = (count / len(df)) * 100.0
        print(f"  {ch:<10} : {count:4d} cases ({pct:.1f}%)")
    print("==================================================\n")

if __name__ == "__main__":
    run_batch_evaluation()
