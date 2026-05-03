import requests
import os
import time
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

# GitHub Secrets se data uthana
WEBAPP_URL = os.environ['GOOGLE_WEBAPP_URL']
TOKEN = os.environ['SECRET_TOKEN']

# --- CONFIGURATION ---
# 'DAILY' = Rozana automation ke liye (7:30 PM trigger)
# 'HISTORICAL' = Purana data upload karne ke liye (Aap 12 din mein 12 mahine kar sakte hain)
MODE = 'DAILY' 

# Agar MODE 'HISTORICAL' hai, toh yahan Dates badlein (Format: YYYY-MM-DD)
START_DATE = "2025-01-01"
END_DATE = "2025-01-31"

def fetch_and_send(target_date):
    date_str = target_date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/content/nsccl/fno_participant_vol_{date_str}.csv"
    
    # ANTI-BOT PROTECTION: NSE ko dikhana ki hum ek browser hain
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # FII row nikalna (Aapke analysis ke liye)
            fii_row = df[df.iloc[:, 0].str.strip() == 'FII'].iloc[0]
            
            payload = {
                "token": TOKEN,
                "date": target_date.strftime("%Y-%m-%d"),
                "client_type": "FII",
                "future_long": int(fii_row.iloc[1]),
                "future_short": int(fii_row.iloc[2]),
                "option_long": int(fii_row.iloc[3]),
                "option_short": int(fii_row.iloc[4])
            }
            res = requests.post(WEBAPP_URL, json=payload)
            print(f"Success for {date_str}: {res.text}")
            return True
        else:
            print(f"Data not ready for {date_str} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"Error for {date_str}: {e}")
        return False

def run_automation():
    if MODE == 'DAILY':
        # 7:30 PM se check shuru karega aur 6 baar koshish karega (Har 10 min mein)
        for attempt in range(6):
            success = fetch_and_send(datetime.now())
            if success: 
                print("Job Completed Successfully.")
                break
            print("NSE data not found. Waiting 10 minutes for next retry...")
            time.sleep(600) 
    
    elif MODE == 'HISTORICAL':
        # Batch Mode: Ek saath poore mahine ka data bhejna
        curr = datetime.strptime(START_DATE, "%Y-%m-%d")
        end = datetime.strptime(END_DATE, "%Y-%m-%d")
        while curr <= end:
            fetch_and_send(curr)
            time.sleep(2) # Anti-bot delay: NSE ko block karne se rokne ke liye
            curr += timedelta(days=1)

if __name__ == "__main__":
    run_automation()
