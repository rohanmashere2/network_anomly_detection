import requests

url = "http://127.0.0.1:8000/predict"

# create dummy input (same length as features)
sample = [1.0]*45   # adjust length if needed

response = requests.post(url, json={"features": sample})

print(response.json())