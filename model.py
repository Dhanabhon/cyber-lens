import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from parser import load_logs_from_txt

# Global model and encoders
isolation_model = None
encoders = {}

# File paths for saved model
MODEL_PATH = "models/isolation_forest.pkl"
ENCODER_PATH = "models/encoders.pkl"

# Convert IP string to integer
def ip_to_int(ip):
    try:
        parts = list(map(int, ip.split('.')))
        return sum([parts[i] << (8 * (3 - i)) for i in range(4)])
    except:
        return 0

# Prepare features for training or inference
def preprocess(df):
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    df['weekday'] = df['timestamp'].dt.weekday
    df['ip_encoded'] = df['ip'].apply(ip_to_int)

    for col in ['user', 'status']:
        if col not in encoders:
            encoders[col] = LabelEncoder()
            df[col + '_encoded'] = encoders[col].fit_transform(df[col])
        else:
            df[col + '_encoded'] = encoders[col].transform(df[col])

    features = df[['hour', 'weekday', 'ip_encoded', 'port', 'user_encoded', 'status_encoded']]
    return features

# Train Isolation Forest and save model
def train_model(df, n_estimators=100, contamination=0.1, random_state=42, save=True):
    global isolation_model
    features = preprocess(df)
    isolation_model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state
    )
    isolation_model.fit(features)
    if save:
        os.makedirs("models", exist_ok=True)
        save_model()

# Predict log risk using trained model
def predict_log_risk(raw_log_path):
    global isolation_model
    if isolation_model is None:
        raise Exception("Model is not loaded. Call load_model() or train_model() first.")

    df = load_logs_from_txt(raw_log_path)
    features = preprocess(df)

    scores = isolation_model.decision_function(features)
    preds = isolation_model.predict(features)

    results = []
    for i, row in df.iterrows():
        risk = "low"
        if preds[i] == -1:
            risk = "high" if row['user'] in ['root', 'admin'] or row['status'] == 'Failed' else "medium"

        results.append({
            "line": f"{row['timestamp']} - {row['user']}@{row['ip']}:{row['port']} [{row['status']}]",
            "risky": preds[i] == -1,
            "risk_level": risk,
            "reason": f"Detected as anomaly (score={scores[i]:.4f})"
        })

    df["risk_level"] = [r["risk_level"] for r in results]
    df["risk_score"] = [r["reason"] for r in results]
    return results, df

# Save model and encoders to disk
def save_model():
    joblib.dump(isolation_model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    print(f"[✓] Model saved to {MODEL_PATH}")
    print(f"[✓] Encoders saved to {ENCODER_PATH}")

# Load model and encoders from disk with error handling
def load_model():
    global isolation_model, encoders
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError("Model files not found. Please train the model first.")
    isolation_model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
    print(f"[✓] Model loaded from {MODEL_PATH}")
    print(f"[✓] Encoders loaded from {ENCODER_PATH}")

# CLI support
if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    df = pd.read_csv("logs/simulated_log.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    train_model(df, n_estimators=150, contamination=0.1)
    print("[✓] Model trained and saved.")
