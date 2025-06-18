import yfinance as yf
import time
from datetime import datetime, timezone
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = 'https://ascpjrfvpizulamxzeiw.supabase.co'  # replace with your URL
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzY3BqcmZ2cGl6dWxhbXh6ZWl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTA2MTcxOSwiZXhwIjoyMDY0NjM3NzE5fQ.yJTIxqEi-Epcxz3JwPR2J59VVF-cj-eKfL_KGarqvPw'        # replace with your key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# List of Indian stock symbols
symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "SBIN.NS",
    "BHARTIARTL.NS", "KOTAKBANK.NS", "AXISBANK.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "WIPRO.NS", "MARUTI.NS", "SUNPHARMA.NS", "HDFCLIFE.NS", "ULTRACEMCO.NS", "NTPC.NS",
    "TECHM.NS", "POWERGRID.NS", "BAJAJFINSV.NS", "NESTLEIND.NS", "TITAN.NS", "ONGC.NS", "COALINDIA.NS",
    "JSWSTEEL.NS", "ADANIENT.NS", "BAJAJ-AUTO.NS", "CIPLA.NS", "HINDALCO.NS", "DRREDDY.NS", "BPCL.NS",
    "GRASIM.NS", "DIVISLAB.NS", "EICHERMOT.NS", "INDUSINDBK.NS", "BRITANNIA.NS", "TATAMOTORS.NS",
    "HEROMOTOCO.NS", "M&M.NS", "SHREECEM.NS", "ADANIPORTS.NS", "SBILIFE.NS", "TATACONSUM.NS", "UPL.NS",
    "ICICIPRULI.NS"
]

def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get("regularMarketPrice")

        if price is None:
            raise ValueError("Price not available")

        return {
            "symbol": symbol,
            "name": info.get("shortName") or info.get("longName") or symbol,
            "price": price,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None

def update_supabase(data):
    try:
        response = supabase.table("stocks").upsert(data).execute()
        if response.data:
            print(f"✅ Updated {data['symbol']}")
        else:
            print(f"❌ Supabase rejected {data['symbol']}: {response}")
    except Exception as e:
        print(f"❌ Error updating {data['symbol']} in Supabase: {e}")

def run_loop():
    while True:
        print("⏳ Fetching and updating stock data...")
        for symbol in symbols:
            data = fetch_stock_data(symbol)
            if data:
                update_supabase(data)
            time.sleep(1.5)  # gentle pacing
        print("✅ All updates complete. Waiting 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    run_loop()
