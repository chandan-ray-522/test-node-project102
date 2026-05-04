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
MODE = 'DAILY'  # पुराना डेटा भरने के लिए 'HISTORICAL' रखें, डेली के लिए 'DAILY'
START_DATE = "2026-03-01" 
END_DATE = "2026-03-31"

# NSE Holiday List 2026
NSE_HOLIDAYS = ["2026-01-15", "2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31", "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", "2026-06-26", "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-10", "2026-11-24", "2026-12-25"]

def fetch_and_send(target_date):
    date_str = target_date.strftime("%d%m%Y")
    url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{date_str}.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # NSE की फाइल से हेडर और डेटा उठाना
            df = pd.read_csv(StringIO(response.text), skiprows=1)
            df.columns = df.columns.str.strip()
            
            header_list = df.columns.tolist()
            all_data = df.values.tolist()
            
            payload = {
                "token": TOKEN, 
                "date": target_date.strftime("%Y-%m-%d"), 
                "headers": header_list,
                "rows": all_data
            }
            requests.post(WEBAPP_URL, json=payload)
            print(f"✅ Full Data for {date_str} sent with Colors.")
            return True
        return False
    except: return False

def run_automation():
    if MODE == 'HISTORICAL':
        curr = datetime.strptime(START_DATE, "%Y-%m-%d")
        end = datetime.strptime(END_DATE, "%Y-%m-%d")
        while curr <= end:
            fetch_and_send(curr)
            time.sleep(2) 
            curr += timedelta(days=1)
            
    elif MODE == 'DAILY':
        today_str = datetime.now().strftime("%Y-%m-%d")
        # Weekend और Holiday चेक
        if datetime.now().weekday() >= 5 or today_str in NSE_HOLIDAYS:
            return
            
        # 7:30 PM to 8:30 PM Retry Loop (10 mins gap)
        for attempt in range(7):
            if fetch_and_send(datetime.now()): break
            time.sleep(600)

if __name__ == "__main__":
    run_automation()
