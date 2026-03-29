import streamlit as st
import json
from datetime import datetime, timedelta
import time
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Network Anomaly Detection", layout="wide")

st.title("🛡️ Network Anomaly Detection")

REFRESH_TIME = 5

try:
    with open("live_log.json", "r") as f:
        logs = json.load(f)

    if len(logs) == 0:
        st.warning("Waiting for data...")
        st.stop()

    # =========================
    # 🔹 GROUP DATA BY MINUTE
    # =========================
    minute_data = {}

    for log in logs:
        if not isinstance(log["time"], (int, float)):
            continue

        ts = datetime.fromtimestamp(log["time"])
        key = ts.strftime("%H:%M")

        if key not in minute_data:
            minute_data[key] = {"normal": 0, "attack": 0}

        if log["prediction"] == 0:
            minute_data[key]["normal"] += 1
        else:
            minute_data[key]["attack"] += 1

    sorted_minutes = sorted(minute_data.keys())

    # =========================
    # 🔹 DATAFRAME FOR GRAPHS
    # =========================
    df = pd.DataFrame([
        {
            "time": m,
            "normal": minute_data[m]["normal"],
            "attack": minute_data[m]["attack"]
        }
        for m in sorted_minutes
    ])

    # =========================
    # 🔹 CURRENT TIME SLOT
    # =========================
    latest_minute = sorted_minutes[-1]
    latest_data = minute_data[latest_minute]

    normal = latest_data["normal"]
    attack = latest_data["attack"]
    total = normal + attack if (normal + attack) > 0 else 1

    attack_percent = (attack / total) * 100

    # Threat level
    if attack_percent > 70:
        threat = "🚨 HIGH"
    elif attack_percent > 40:
        threat = "⚠️ MEDIUM"
    else:
        threat = "🟢 LOW"

    # Time slot label
    start_time = datetime.strptime(latest_minute, "%H:%M")
    end_time = start_time + timedelta(minutes=1)
    slot_label = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

    # =========================
    # 🔹 TOP METRICS
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🚨 Attacks", attack)
    col2.metric("🟢 Normal", normal)
    col3.metric("📊 Attack %", f"{attack_percent:.1f}%")
    col4.metric("🔥 Threat Level", threat)

    st.divider()

    # =========================
    # 🔹 CURRENT SLOT DISPLAY
    # =========================
    st.subheader("⏱️ Current Time Slot")

    c1, c2, c3 = st.columns(3)

    c1.metric("🟢 Normal", normal)
    c2.metric("🚨 Attack", attack)

    if attack > normal:
        c3.error("🚨 Under Attack")
    else:
        c3.success("🟢 Safe")

    st.caption(f"Time Window: {slot_label}")

    st.divider()

    # =========================
    # 🔹 LATEST DETECTION
    # =========================
    st.subheader("🧠 Latest Detection")

    latest_log = logs[-1]

    if latest_log["prediction"] == 1:
        st.error(latest_log["message"])
    else:
        st.success(latest_log["message"])

    st.divider()

    # =========================
    # 🔹 SMALL GRAPHS
    # =========================
    st.subheader("📈 Traffic Analytics")

    col1, col2 = st.columns(2)

    # Graph 1: Trend
    with col1:
        st.caption("Traffic Trend")

        fig1, ax1 = plt.subplots(figsize=(4, 3))
        ax1.plot(df["time"], df["normal"], label="Normal")
        ax1.plot(df["time"], df["attack"], label="Attack")
        ax1.set_title("Trend")
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()

        st.pyplot(fig1)

    # Graph 2: Distribution
    with col2:
        st.caption("Traffic Distribution")

        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.pie(
            [normal, attack],
            labels=["Normal", "Attack"],
            autopct="%1.1f%%"
        )
        ax2.set_title("Distribution")

        st.pyplot(fig2)

    st.divider()

    # =========================
    # 🔹 HISTORY (EXCLUDE CURRENT)
    # =========================
    st.subheader("📊 Previous Time Slots")

    history_minutes = sorted_minutes[:-1][::-1]

    for m in history_minutes[:10]:
        data = minute_data[m]

        start = datetime.strptime(m, "%H:%M")
        end = start + timedelta(minutes=1)

        label = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"

        c1, c2, c3 = st.columns([2,1,1])

        c1.write(f"⏱️ {label}")
        c2.metric("🟢 Normal", data["normal"])
        c3.metric("🚨 Attack", data["attack"])

    # =========================
    # 🔹 ALERT SYSTEM
    # =========================
    if attack_percent > 70:
        st.error("🚨 CRITICAL ALERT: High attack traffic!")
    elif attack_percent > 40:
        st.warning("⚠️ Suspicious activity detected!")

except FileNotFoundError:
    st.warning("Waiting for live_log.json...")

except Exception as e:
    st.error(f"Error: {e}")

# 🔄 AUTO REFRESH
time.sleep(REFRESH_TIME)
st.rerun()