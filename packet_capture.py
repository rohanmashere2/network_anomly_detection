from scapy.all import sniff
import requests
import joblib
import time

URL = "http://127.0.0.1:8000/predict"

feature_names = joblib.load("feature_names.pkl")
SIZE = len(feature_names)

packet_buffer = []
last_sent_time = time.time()

def extract_features(buffer):
    features = [0] * SIZE

    total_packets = len(buffer)
    total_bytes = sum(len(p) for p in buffer)
    duration = 2  # fixed window

    rate = total_packets / duration if duration > 0 else 0

    features[0] = duration
    features[1] = total_bytes
    features[3] = total_packets
    features[5] = rate

    return features

def process(packet):
    global packet_buffer, last_sent_time

    packet_buffer.append(packet)

    current_time = time.time()

    # 🔥 Every 2 seconds → send prediction
    if current_time - last_sent_time >= 2:

        if len(packet_buffer) > 0:
            features = extract_features(packet_buffer)

            try:
                res = requests.post(URL, json={"features": features})
                print(res.json())
            except:
                print("API error")

        packet_buffer = []
        last_sent_time = current_time

print("🚀 Capturing traffic (real-time)...")
sniff(prn=process, store=False)