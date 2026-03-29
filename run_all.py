import subprocess
import time

print("🚀 Starting system...")

api = subprocess.Popen(["uvicorn", "app:app", "--reload"])
time.sleep(5)

dashboard = subprocess.Popen(["streamlit", "run", "dashboard.py"])
time.sleep(5)

packet = subprocess.Popen(["python", "packet_capture.py"])

print("✅ System running!")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
    api.terminate()
    dashboard.terminate()
    packet.terminate()