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
MODE = 'HISTORICAL' # एक महीने का डेटा भरने के लिए 'HISTORICAL' रखें। रोज़ाना के लिए 'DAILY'
START_DATE = "2026-04-01" 
END_DATE = "2026-04-30"

# NSE Holiday List 2026 (As per image_56.png)
NSE_HOLIDAYS = ["2026-01-15", "2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31", "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", "2026-06-26", "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-10", "2026-11-24", "2026-12-25"]

def fetch_and_send(target_date):
    date_str = target_date.strftime("%d%m%Y")
    url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{date_str}.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            participants = ['Client', 'DII', 'FII', 'Pro'] #
            data_to_send = []
            
            for p in participants:
                row = df[df.iloc[:, 0].str.strip() == p].iloc[0]
                # Date, Type, Future Long, Future Short, Call Long, Put Long, Call Short, Put Short
                data_to_send.append([
                    target_date.strftime("%Y-%m-%d"), p, 
                    int(row.iloc[1]), int(row.iloc[2]), # Future Index Long/Short
                    int(row.iloc[5]), int(row.iloc[6]), # Option Index Call/Put Long
                    int(row.iloc[7]), int(row.iloc[8])  # Option Index Call/Put Short
                ])
            
            payload = {"token": TOKEN, "date": target_date.strftime("%Y-%m-%d"), "rows": data_to_send}
            requests.post(WEBAPP_URL, json=payload)
            print(f"✅ Data for {date_str} sent successfully.")
            return True
        return False
    except: return False

def run_automation():
    if MODE == 'HISTORICAL':
        print(f"🚀 Running Historical for {START_DATE} to {END_DATE}")
        curr = datetime.strptime(START_DATE, "%Y-%m-%d")
        end = datetime.strptime(END_DATE, "%Y-%m-%d")
        while curr <= end:
            fetch_and_send(curr)
            time.sleep(2) 
            curr += timedelta(days=1)
            
    elif MODE == 'DAILY':
        today_str = datetime.now().strftime("%Y-%m-%d")
        if datetime.now().weekday() >= 5 or today_str in NSE_HOLIDAYS: #
            print("Market Closed Today.")
            return
            
        # 7:30 PM to 8:30 PM Retry Loop (Runs for 60 mins, checks every 10 mins)
        print(f"🕒 Checking for Today's Data ({today_str})...")
        for attempt in range(7): # 0 to 6 = 7 times
            if fetch_and_send(datetime.now()):
                break
            if attempt < 6:
                print(f"Data not ready. Retrying in 10 mins... (Attempt {attempt+1}/7)")
                time.sleep(600) # 10 Minute Wait

if __name__ == "__main__":
    run_automation()
