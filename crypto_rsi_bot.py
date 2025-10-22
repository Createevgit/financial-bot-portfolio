"""
Crypto RSI Bot by Createev Tech
--------------------------------
This simulated trading bot analyzes crypto market data using the Relative Strength Index (RSI).
It’s designed for learning and demonstration only — not live trading.
"""

import requests
import pandas as pd
import time

def fetch_crypto_data(symbol="BTCUSDT", interval="1h", limit=100):
    """Fetch historical crypto data from Binance API."""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    frame = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'trades', 'tb_base', 'tb_quote', 'ignore'
    ])
    frame['close'] = frame['close'].astype(float)
    return frame

def calculate_rsi(prices, period=14):
    """Compute RSI from closing prices."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def trading_signal(rsi):
    """Generate basic trading signals based on RSI."""
    if rsi < 30:
        return "BUY"
    elif rsi > 70:
        return "SELL"
    else:
        return "HOLD"

def run_bot():
    data = fetch_crypto_data()
    data['RSI'] = calculate_rsi(data['close'])
    latest_rsi = data['RSI'].iloc[-1]
    action = trading_signal(latest_rsi)

    print(f"Latest RSI: {latest_rsi:.2f} → Action: {action}")

if __name__ == "__main__":
    print("🚀 Starting Crypto RSI Bot by Createev Tech")
    while True:
        run_bot()
        time.sleep(60 * 60)  # run hourly
