import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

# Supabase credentials
SUPABASE_URL = 'https://ascpjrfvpizulamxzeiw.supabase.co'  # replace with your URL
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzY3BqcmZ2cGl6dWxhbXh6ZWl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTA2MTcxOSwiZXhwIjoyMDY0NjM3NzE5fQ.yJTIxqEi-Epcxz3JwPR2J59VVF-cj-eKfL_KGarqvPw'        # replace with your key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def auto_exit_trades():
    try:
        # 1️⃣ Fetch all open trades that have stop_loss or take_profit set
        open_trades = supabase.table('trades').select("*").eq("status", "open").execute().data

        for trade in open_trades:
            symbol = trade['stock_symbol']
            sl = trade.get('stop_loss')
            tp = trade.get('take_profit')

            if sl is None and tp is None:
                continue  # Skip trades without SL or TP

            # 2️⃣ Get current price of the stock from your `stocks` table
            stock_data = supabase.table('stocks').select("price").eq("symbol", symbol).single().execute().data
            if not stock_data:
                print(f"No stock data found for {symbol}")
                continue

            current_price = float(stock_data['price'])
            entry_price = float(trade['price'])
            quantity = int(trade['quantity'])
            leverage = float(trade.get('leverage', 1))
            is_buy = trade['trade_type'] == 'Buy'

            # 3️⃣ Check SL or TP conditions
            sl_hit = False
            tp_hit = False

            if is_buy:
                if sl is not None and current_price <= sl:
                    sl_hit = True
                if tp is not None and current_price >= tp:
                    tp_hit = True
            else:  # Sell trade
                if sl is not None and current_price >= sl:
                    sl_hit = True
                if tp is not None and current_price <= tp:
                    tp_hit = True

            if not sl_hit and not tp_hit:
                continue  # Neither hit, skip

            # 4️⃣ Calculate PnL
            if is_buy:
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity

            # 5️⃣ Update trade status
            supabase.table('trades').update({
                'status': 'closed',
                'exit_price': current_price,
                'closed_at': datetime.now().isoformat(),
                'pnl': pnl
            }).eq('id', trade['id']).execute()

            # 6️⃣ Refund cost + PnL to user balance
            user_id = trade['user_id']
            cost = (entry_price * quantity) / leverage

            user_data = supabase.table('users').select("demo_balance").eq("id", user_id).single().execute().data
            current_balance = float(user_data['demo_balance'])

            new_balance = current_balance + cost + pnl

            supabase.table('users').update({
                'demo_balance': new_balance
            }).eq('id', user_id).execute()

            print(f"✅ Trade ID {trade['id']} auto-exited at ₹{current_price} | P&L: ₹{pnl:.2f}")

    except Exception as e:
        print("❌ Error during auto-exit:", e)


if __name__ == "__main__":
    auto_exit_trades()
