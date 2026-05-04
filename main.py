import requests
import os
import time
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

# GitHub Secrets
WEBAPP_URL = os.environ['GOOGLE_WEBAPP_URL']
TOKEN = os.environ['SECRET_TOKEN']

# --- CONFIGURATION ---
MODE = 'DAILY' 
START_DATE = "2026-04-01"
END_DATE = "2026-04-30"

# NSE Holiday List 2026 (As per your image)
NSE_HOLIDAYS = ["2026-01-15", "2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31", "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", "2026-06-26", "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-10", "2026-11-24", "2026-12-25"]

def fetch_and_send(target_date):
    date_str = target_date.strftime("%d%m%Y")
    url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{date_str}.csv"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            
            # Charon participants ki list
            participants = ['Client', 'DII', 'FII', 'Pro']
            all_rows_data = []

            for p in participants:
                # Row find karna aur columns extract karna (Index specific)
                row = df[df.iloc[:, 0].str.strip() == p].iloc[0]
                all_rows_data.append({
                    "client_type": p,
                    "future_long": int(row.iloc[1]),
                    "future_short": int(row.iloc[2]),
                    "opt_call_long": int(row.iloc[5]),
                    "opt_put_long": int(row.iloc[6]),
                    "opt_call_short": int(row.iloc[7]),
                    "opt_put_short": int(row.iloc[8])
                })
            
            # Pura data ek sath bhejna
            payload = {
                "token": TOKEN,
                "date": target_date.strftime("%Y-%m-%d"),
                "rows": all_rows_data
            }
            res = requests.post(WEBAPP_URL, json=payload)
            print(f"✅ Full Data pushed for {date_str}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

def run_automation():
    today_str = datetime.now().strftime("%Y-%m-%d")
    if MODE == 'HISTORICAL':
        if datetime.now().weekday() >= 5 or today_str in NSE_HOLIDAYS:
            return
        for attempt in range(6):
            if fetch_and_send(datetime.now()): break
            time.sleep(600)
    elif MODE == 'HISTORICAL':
        curr = datetime.strptime(START_DATE, "2026-04-01")
        end = datetime.strptime(END_DATE, "2026-04-30")
        while curr <= end:
            fetch_and_send(curr)
            time.sleep(2) 
            curr += timedelta(days=1)

if __name__ == "__main__":
    run_automation()
