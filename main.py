import requests
import os
import json
from datetime import datetime

# GitHub Secrets se data uthana
WEBAPP_URL = os.environ['GOOGLE_WEBAPP_URL']
TOKEN = os.environ['SECRET_TOKEN']

def fetch_and_send():
    # Aaj ki date nikalna (NSE format ke liye)
    today = datetime.now().strftime("%d%m%Y")
    
    # Example NSE Archival Link (Isme hum parameters badal sakte hain)
    # Note: Filhal hum test data bhej rahe hain ye check karne ke liye ki connection sahi hai ya nahi
    test_data = {
        "token": TOKEN,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "client_type": "FII",
        "future_long": 12345,
        "future_short": 6789,
        "option_long": 55555,
        "option_short": 44444
    }

    # Google Sheet Web App ko data bhejna
    response = requests.post(WEBAPP_URL, json=test_data)
    print(f"Status: {response.text}")

if __name__ == "__main__":
    fetch_and_send()
