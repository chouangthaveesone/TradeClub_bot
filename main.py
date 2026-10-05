import os
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def check_cdc_signal(symbol_name, df):
    # ຄຳນວນ EMA / SMA
    df['ema1'] = ta.ema(ta.ema(df['Close'], length=12), length=1)
    df['ema2'] = ta.ema(ta.ema(df['Close'], length=26), length=1)
    df['ema50'] = ta.ema(df['Close'], length=50)
    df['sma200'] = ta.sma(df['Close'], length=200)

    # ສັນຍານ Buy / Sell ຫຼັກ
    buy_signal = (df['ema1'].iloc[-1] > df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] <= df['ema2'].iloc[-2])
    sell_signal = (df['ema1'].iloc[-1] < df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] >= df['ema2'].iloc[-2])

    if buy_signal:
        send_telegram(f"🟢 *[CDC Alert]* {symbol_name}\nBUY Signal Detected!")
    elif sell_signal:
        send_telegram(f"🔴 *[CDC Alert]* {symbol_name}\nSELL Signal Detected!")

# ດຶງຂໍ້ມູນຄູ່ເທຣດ (BTC-USD, GC=F ສຳລັບ XAUUSD, EURUSD=X)
pairs = {"BTCUSD": "BTC-USD", "XAUUSD": "GC=F", "EURUSD": "EURUSD=X"}

for name, ticker in pairs.items():
    data = yf.download(ticker, period="5d", interval="15m")
    if not data.empty:
        check_cdc_signal(name, data)