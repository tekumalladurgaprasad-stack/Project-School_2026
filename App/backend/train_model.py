"""
Model training and serialization script for CrediGuard.
Trains a Random Forest classifier on default_of_credit_card_clients.xls
with cost-sensitive threshold optimization and exports random_forest_credit_default.pkl.
"""
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_and_export():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    dataset_path = os.path.join(root_dir, "default_of_credit_card_clients.xls")
    
    if not os.path.exists(dataset_path):
        dataset_path = "default_of_credit_card_clients.xls"
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Could not locate dataset file: {dataset_path}")
        
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_excel(dataset_path, header=1, engine="calamine")
    df = df.drop(columns=["ID"])
    df = df.rename(columns={"PAY_0": "PAY_1", "default payment next month": "DEFAULT"})
    df["EDUCATION"] = df["EDUCATION"].replace({0: 5, 6: 5})
    df = pd.get_dummies(df, columns=["EDUCATION", "MARRIAGE"], drop_first=True, dtype=int)
    df["SEX"] = df["SEX"].map({1: 0, 2: 1})

    X = df.drop(columns="DEFAULT")
    y = df["DEFAULT"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train, y_train, test_size=0.2, stratify=y_train, random_state=42
    )

    best_params = {
        "n_estimators": 150,
        "max_depth": None,
        "max_features": 0.7,
        "min_samples_leaf": 1,
        "min_samples_split": 5,
    }

    print("Training RandomForestClassifier...")
    rf = RandomForestClassifier(**best_params, random_state=42, n_jobs=-1)
    rf.fit(X_fit, y_fit)

    # Optimal threshold from business cost validation sweep (FN cost: 5, FP cost: 1)
    best_threshold = 0.1779
    output_path = os.path.join(base_dir, "random_forest_credit_default.pkl")
    joblib.dump({
        "model": rf,
        "threshold": best_threshold,
        "params": best_params,
        "features": list(X.columns),
        "fn_cost": 5,
        "fp_cost": 1,
    }, output_path)
    print(f"Model saved successfully -> {output_path}")

if __name__ == "__main__":
    train_and_export()
