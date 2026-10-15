import os
import requests
import pandas as pd
import yfinance as yf

# ดຶງຄ່າ Telegram Token ແລະ Chat ID ຈາກ Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    """ฟັງຊັນສຳລັບສົ່ງຂໍ້ຄວາມເຂົ້າ Telegram Group"""
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID, 
            "text": msg, 
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"Error sending request to Telegram: {e}")

def check_cdc_signal(symbol_name, df):
    """ຄຳນວນສັນຍານ CDC ActionZone ດ້ວຍ Pandas ມາດຕະຖານ"""
    # ປ້ອງກັນກໍລະນີ DataFrame ສັ້ນເກີນໄປ
    if len(df) < 200:
        print(f"Data for {symbol_name} is not enough for calculation.")
        return

    # ຄຳນວນ EMA / SMA ດ້ວຍ Pandas ມາດຕະຖານ
    df['ema1'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema2'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['sma200'] = df['Close'].rolling(window=200).mean()

    # ตรวจสอบເງື່ອນໄຂ Buy / Sell Signal
    buy_signal = (df['ema1'].iloc[-1] > df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] <= df['ema2'].iloc[-2])
    sell_signal = (df['ema1'].iloc[-1] < df['ema2'].iloc[-1]) and (df['ema1'].iloc[-2] >= df['ema2'].iloc[-2])

    current_price = df['Close'].iloc[-1]

    if buy_signal:
        message = f"🟢 *[CDC ActionZone Alert]*\nSymbol: `{symbol_name}`\nSignal: *BUY*\nPrice: `{current_price:.2f}`"
        send_telegram(message)
        print(f"BUY Signal sent for {symbol_name}")
    elif sell_signal:
        message = f"🔴 *[CDC ActionZone Alert]*\nSymbol: `{symbol_name}`\nSignal: *SELL*\nPrice: `{current_price:.2f}`"
        send_telegram(message)
        print(f"SELL Signal sent for {symbol_name}")
    else:
        print(f"No signal for {symbol_name} (Price: {current_price:.2f})")

def main():
    # กำหนดຄູ່ເທຣດที่ต้องการກວດສອບ
    pairs = {
        "BTCUSD": "BTC-USD", 
        "XAUUSD": "GC=F", 
        "EURUSD": "EURUSD=X"
    }

    for name, ticker in pairs.items():
        try:
            print(f"Fetching data for {name} ({ticker})...")
            data = yf.download(ticker, period="5d", interval="15m", progress=False)
            
            if not data.empty:
                # ປ້ອງກັນກໍລະນີ yfinance ສົ່ງ DataFrame ມາແບບ MultiIndex Columns
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                    
                check_cdc_signal(name, data)
            else:
                print(f"No data returned for {name}")
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main()
