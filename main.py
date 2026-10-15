import os
import requests
import pandas as pd
import yfinance as yf

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def check_cdc_signal(symbol_name, df):
    # ຄຳນວນ EMA / SMA
    df['ema1'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema2'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['sma200'] = df['Close'].rolling(window=200).mean()

    buy_signal = (df['ema1'].iloc[-1] > df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] <= df['ema2'].iloc[-2])
    sell_signal = (df['ema1'].iloc[-1] < df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] >= df['ema2'].iloc[-2])
    current_price = df['Close'].iloc[-1]

    if buy_signal:
        send_telegram(f"🟢 *[CDC ActionZone Alert]*\nSymbol: `{symbol_name}`\nSignal: *BUY*\nPrice: `{current_price:.2f}`")
    elif sell_signal:
        send_telegram(f"🔴 *[CDC ActionZone Alert]*\nSymbol: `{symbol_name}`\nSignal: *SELL*\nPrice: `{current_price:.2f}`")

def main():
    # ປະກາດຕົວແປ pairs ໄວ້ໃນຟັງຊັນ main()
    pairs = {
        "BTCUSD": "BTC-USD", 
        "XAUUSD": "GC=F", 
        "EURUSD": "EURUSD=X"
    }

    for name, ticker in pairs.items():
        data = yf.download(ticker, period="5d", interval="15m", progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            check_cdc_signal(name, data)

if __name__ == "__main__":
    main()
