import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline

# Import from backend
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.ml.feature_engineering import build_feature_preprocessor, prepare_features_df
from app.ml.evaluation import evaluate_binary_classifier

def train_and_evaluate_models():
    data_path = os.path.join(project_root, "data", "recovery_training_data.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at {data_path}. Run generate_dataset.py first.")

    df = pd.read_csv(data_path)
    X = prepare_features_df(df)

    targets = {
        "email": "email_recovery_success",
        "whatsapp": "whatsapp_recovery_success",
        "voice": "voice_recovery_success"
    }

    models_dir = os.path.join(backend_path, "models_ml")
    os.makedirs(models_dir, exist_ok=True)

    metrics_output = {
        "trained_at": datetime.utcnow().isoformat(),
        "dataset_size": len(df),
        "random_seed": 42,
        "test_split_ratio": 0.2,
        "models": {}
    }

    print("==================================================")
    print("REVENUESHIELD AI — CHANNEL MODEL TRAINING")
    print("==================================================")

    for ch_name, target_col in targets.items():
        y = df[target_col].values
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        preprocessor = build_feature_preprocessor()
        classifier = GradientBoostingClassifier(n_estimators=100, random_state=42, learning_rate=0.1)
        
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        eval_results = evaluate_binary_classifier(y_test, y_pred, y_prob)
        metrics_output["models"][ch_name] = eval_results

        # Save model pipeline artifact
        model_filename = f"{ch_name}_recovery_model.joblib"
        model_path = os.path.join(models_dir, model_filename)
        joblib.dump(pipeline, model_path)

        print(f"[{ch_name.upper()} MODEL]")
        print(f"  Accuracy  : {eval_results['accuracy']:.4f}")
        print(f"  Precision : {eval_results['precision']:.4f}")
        print(f"  Recall    : {eval_results['recall']:.4f}")
        print(f"  F1 Score  : {eval_results['f1']:.4f}")
        print(f"  ROC-AUC   : {eval_results['roc_auc']:.4f}")
        print(f"  Saved to  : {model_path}\n")

    # Save machine-readable metrics
    json_metrics_path = os.path.join(backend_path, "model_metrics.json")
    with open(json_metrics_path, "w") as f:
        json.dump(metrics_output, f, indent=2)

    # Save docs/evaluation.md
    docs_dir = os.path.join(project_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    md_eval_path = os.path.join(docs_dir, "evaluation.md")
    
    with open(md_eval_path, "w") as f:
        f.write(generate_evaluation_markdown(metrics_output))

    print(f"Saved machine-readable metrics to {json_metrics_path}")
    print(f"Saved evaluation report to {md_eval_path}")

def generate_evaluation_markdown(metrics: dict) -> str:
    md = f"""# RevenueShield AI — ML Model Evaluation Report

**Trained At:** `{metrics['trained_at']}`  
**Dataset Size:** {metrics['dataset_size']} synthetic records  
**Random Seed:** {metrics['random_seed']}  
**Train/Test Split:** 80% / 20% Stratified  

> [!NOTE]
> **Dataset Assumption & Disclaimer:**  
> This evaluation was performed on a synthetic payment failure recovery dataset generated specifically for the Razorpay AI Buildathon. Metrics reflect model capacity to learn probabilistic recovery patterns on simulated data and are not claims of live production performance.

---

## Performance Summary Table

| Recovery Channel | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for ch, m in metrics["models"].items():
        md += f"| **{ch.upper()}** | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['roc_auc']:.4f} |\n"

    md += "\n---\n\n## Confusion Matrices\n\n"
    for ch, m in metrics["models"].items():
        cm = m["confusion_matrix"]
        md += f"""### {ch.upper()} Channel Model
- **True Negatives (TN):** {cm['true_negatives']}
- **False Positives (FP):** {cm['false_positives']}
- **False Negatives (FN):** {cm['false_negatives']}
- **True Positives (TP):** {cm['true_positives']}

"""
    return md

if __name__ == "__main__":
    train_and_evaluate_models()
