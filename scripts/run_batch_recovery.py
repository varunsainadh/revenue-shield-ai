import os
import sys
import pandas as pd
import numpy as np

# Setup python path for backend imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.database import init_db, SessionLocal
from app.services.recovery_service import RecoveryService
from app.models.recovery_case_model import RecoveryCaseModel

def run_batch_simulation():
    init_db()
    db = SessionLocal()
    try:
        data_path = os.path.join(project_root, "data", "recovery_training_data.csv")
        if not os.path.exists(data_path):
            from scripts.generate_dataset import generate_dataset
            generate_dataset(num_records=1000)

        df = pd.read_csv(data_path).head(100)
        rec_service = RecoveryService(db)

        print("==================================================")
        print("REVENUESHIELD AI — BATCH RECOVERY SIMULATION")
        print("==================================================")
        print(f"Ingesting and processing {len(df)} failed payment events...\n")

        analyzed_count = 0
        executed_count = 0
        manual_review_count = 0
        blocked_count = 0
        recovered_count = 0

        for _, row in df.iterrows():
            row_dict = row.to_dict()
            case = rec_service.create_case(row_dict)

            if case.status in ["RECOVERED", "STOPPED"]:
                continue

            try:
                analyzed = rec_service.analyze_case(case.id)
                analyzed_count += 1

                if analyzed.status == "ACTION_READY":
                    res = rec_service.execute_recovery(case.id)
                    if res.get("executed"):
                        executed_count += 1
                        
                        rec_ch_lower = case.recommended_channel.lower()
                        label_col = f"{rec_ch_lower}_recovery_success"
                        
                        if row_dict.get(label_col, 0) == 1:
                            rec_service.process_payment_success(case.id, channel_override=case.recommended_channel)
                            recovered_count += 1
                elif analyzed.status == "MANUAL_REVIEW":
                    manual_review_count += 1
                elif analyzed.status == "STOPPED":
                    blocked_count += 1
            except Exception as e:
                pass

        # Calculate Batch Metrics
        total_tx = db.query(RecoveryCaseModel).count()
        rev_at_risk = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status != "STOPPED").all()
        tot_risk_amt = sum(c.amount for c in rev_at_risk) if rev_at_risk else 0.0
        
        recovered_cases = db.query(RecoveryCaseModel).filter(RecoveryCaseModel.status == "RECOVERED").all()
        gross_recovered = sum(c.amount for c in recovered_cases) if recovered_cases else 0.0
        rec_rate = (len(recovered_cases) / total_tx) * 100.0 if total_tx else 0.0
        rec_eff = (gross_recovered / tot_risk_amt) * 100.0 if tot_risk_amt else 0.0

        print("--- BATCH RECOVERY BUSINESS METRICS ---")
        print(f"  Total Transactions Ingested : {total_tx:4d}")
        print(f"  Revenue At Risk             : INR {tot_risk_amt:,.2f}")
        print(f"  Cases Analyzed              : {analyzed_count:4d}")
        print(f"  Interventions Executed      : {executed_count:4d}")
        print(f"  Manual Reviews Required     : {manual_review_count:4d}")
        print(f"  Blocked Risk Cases          : {blocked_count:4d}")
        print(f"  Successful Recoveries       : {len(recovered_cases):4d}")
        print(f"  Gross Recovered Revenue     : INR {gross_recovered:,.2f}")
        print(f"  Recovery Rate               : {rec_rate:.2f}%")
        print(f"  Recovery Efficiency         : {rec_eff:.2f}%\n")

        print("==================================================")
        print("BATCH RECOVERY COMPLETE — ALL METRICS UPDATED")
        print("==================================================")
    finally:
        db.close()

if __name__ == "__main__":
    run_batch_simulation()
