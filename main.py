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
MODE = 'DAILY' # 'HISTORICAL' bharne ke liye badlein
START_DATE = "2026-04-01"
END_DATE = "2026-04-30"

# --- NSE HOLIDAY LIST 2026 (Strictly as per your image_56.png) ---
NSE_HOLIDAYS = [
    "2026-01-15", # Municipal Corporation Election
    "2026-01-26", # Republic Day
    "2026-03-03", # Holi
    "2026-03-26", # Shri Ram Navami
    "2026-03-31", # Shri Mahavir Jayanti
    "2026-04-03", # Good Friday
    "2026-04-14", # Dr. Baba Saheb Ambedkar Jayanti
    "2026-05-01", # Maharashtra Day
    "2026-05-28", # Bakri Id
    "2026-06-26", # Muharram
    "2026-09-14", # Ganesh Chaturthi
    "2026-10-02", # Mahatma Gandhi Jayanti
    "2026-10-20", # Dussehra
    "2026-11-10", # Diwali-Balipratipada
    "2026-11-24", # Guru Nanak Jayanti
    "2026-12-25"  # Christmas
]

def fetch_and_send(target_date):
    date_str = target_date.strftime("%d%m%Y")
    url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{date_str}.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
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
            print(f"✅ Data pushed for {date_str}")
            return True
        elif response.status_code == 404:
            print(f"⚪ 404: No data found for {date_str}")
            return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

def run_automation():
    today_str = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().weekday()

    if MODE == 'DAILY':
        # TRIPLE SECURITY CHECK
        # 1. Weekend Check (Sat/Sun)
        # 2. Holiday Check (NSE Calendar)
        if weekday >= 5 or today_str in NSE_HOLIDAYS:
            print(f"🛑 Market is Closed today ({today_str}). No requests sent to NSE.")
            return
        
        print(f"🚀 Starting Daily Run for {today_str}...")
        for attempt in range(6):
            if fetch_and_send(datetime.now()): break
            print("NSE data not ready. Retrying in 10 mins...")
            time.sleep(600)
    
    elif MODE == 'HISTORICAL':
        # Historical mode mein koi rok-tok nahi, taaki aap chutti mein data bhar sakein
        print(f"📂 Starting Historical Fetch: {START_DATE} to {END_DATE}")
        curr = datetime.strptime(START_DATE, "%Y-%m-%d")
        end = datetime.strptime(END_DATE, "%Y-%m-%d")
        while curr <= end:
            # Historical mein robot weekends/holidays ko skip nahi karega, 
            # bas file check karega (404 aane par safe skip karega)
            fetch_and_send(curr)
            time.sleep(2) 
            curr += timedelta(days=1)

if __name__ == "__main__":
    run_automation()
