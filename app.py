from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np
import json
import time

app = FastAPI()

model = joblib.load("unsw_model.pkl")
scaler = joblib.load("scaler.pkl")

class InputData(BaseModel):
    features: List[float]

# 🔥 RULE-BASED DETECTION (REALISTIC)
def rule_detection(features):
    dur = features[0]
    total_bytes = features[1]
    total_packets = features[3]
    rate = features[5]

    # DDoS-like behavior
    if rate > 800 or total_packets > 800:
        return 1, "🚨 High Traffic Spike (Possible DDoS)", "HIGH"

    # Bot-like behavior
    elif dur < 1 and total_packets > 200:
        return 1, "⚠️ Burst Traffic (Bot Activity)", "MEDIUM"

    # Suspicious
    elif total_bytes > 500000:
        return 1, "⚠️ Unusual Data Transfer", "LOW"

    return 0, "✅ Normal Traffic", "SAFE"

@app.post("/predict")
def predict(data: InputData):

    features = data.features

    # =========================
    # 🔥 RULE-BASED DETECTION FIRST
    # =========================
    rule_pred, rule_msg, severity = rule_detection(features)

    # =========================
    # 🔥 ML PREDICTION (SECONDARY)
    # =========================
    arr = np.array(features).reshape(1, -1)
    arr = scaler.transform(arr)

    ml_pred = model.predict(arr)[0]

    # =========================
    # 🔥 FINAL DECISION
    # =========================
    if rule_pred == 1:
        final_pred = 1
        message = rule_msg
    else:
        final_pred = ml_pred
        message = "🚨 ML Detected Attack" if ml_pred == 1 else "✅ Normal Traffic"

    result = {
        "time": time.time(),
        "prediction": int(final_pred),
        "message": message,
        "severity": severity
    }

    # =========================
    # LOGGING
    # =========================
    try:
        with open("live_log.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(result)
    logs = logs[-500:]

    with open("live_log.json", "w") as f:
        json.dump(logs, f)

    return result