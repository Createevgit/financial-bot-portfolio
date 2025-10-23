"""
Createev Tech — Crypto Market Demo Trading Bot (Simulation)
Safe demo: fetches Binance public klines (no API key), computes indicators,
generates buy/sell signals and simulates account P/L. NOT for live trading.

Author: Tomiwa Samuel / Createev Tech
"""

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ---------- Config ----------
SYMBOL = "BTCUSDT"         # pair to simulate
INTERVAL = "1h"            # Binance interval: 1m,3m,5m,15m,1h,4h,1d...
LIMIT = 500                # number of candles to fetch (max 1000 typical)
RSI_PERIOD = 14
SMA_SHORT = 10
SMA_LONG = 50
STARTING_BALANCE = 10000.0 # simulated USD balance
POSITION_SIZE = 0.05       # fraction of balance per trade (5%)
SLEEP_SECONDS = 0          # set >0 to loop continuously; 0 -> single run
# ----------------------------

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

def fetch_klines(symbol=SYMBOL, interval=INTERVAL, limit=LIMIT):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(BINANCE_KLINES, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","quote_av","trades","tb_base_av","tb_quote_av","ignore"
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['open'] = df['open'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def simulate_trading(df):
    df['rsi'] = compute_rsi(df['close'], RSI_PERIOD)
    df['sma_short'] = df['close'].rolling(window=SMA_SHORT, min_periods=1).mean()
    df['sma_long'] = df['close'].rolling(window=SMA_LONG, min_periods=1).mean()

    balance = STARTING_BALANCE
    position = 0.0
    entry_price = None
    trade_log = []

    for i in range(max(SMA_LONG, RSI_PERIOD), len(df)):
        row = df.iloc[i]
        price = row['close']
        rsi = row['rsi']
        sma_short = row['sma_short']
        sma_long = row['sma_long']

        buy_signal = (rsi < 35) and (sma_short > sma_long)
        sell_signal = (rsi > 65) or (sma_short < sma_long)

        if buy_signal and position == 0:
            usd_to_use = balance * POSITION_SIZE
            position = usd_to_use / price
            balance -= usd_to_use
            entry_price = price
            trade_log.append({
                "time": row['open_time'],
                "type": "BUY",
                "price": price,
                "position": position,
                "balance": balance
            })
        elif sell_signal and position > 0:
            proceeds = position * price
            pnl = proceeds - (position * entry_price)
            balance += proceeds
            trade_log.append({
                "time": row['open_time'],
                "type": "SELL",
                "price": price,
                "position": position,
                "pnl": pnl,
                "balance": balance
            })
            position = 0.0
            entry_price = None

    final_price = df['close'].iloc[-1]
    portfolio_value = balance + position * final_price
    returns_pct = (portfolio_value / STARTING_BALANCE - 1) * 100

    result = {
        "starting_balance": STARTING_BALANCE,
        "final_balance": round(balance, 2),
        "asset_position": position,
        "asset_value": round(position * final_price, 2),
        "portfolio_value": round(portfolio_value, 2),
        "returns_pct": round(returns_pct, 2),
        "last_price": final_price,
        "trades": trade_log
    }
    return result

def pretty_print_result(res):
    print("===== Createev Tech — Crypto Demo Bot (Simulation) =====")
    print(f"Symbol: {SYMBOL} | Interval: {INTERVAL}")
    print(f"Last price: {res['last_price']:.2f} USD")
    print(f"Starting balance: ${res['starting_balance']:.2f}")
    print(f"Final cash balance: ${res['final_balance']:.2f}")
    print(f"Asset position: {res['asset_position']:.8f} units (value ${res['asset_value']:.2f})")
    print(f"Portfolio value: ${res['portfolio_value']:.2f}")
    print(f"Total return: {res['returns_pct']:.2f}%")
    print("Recent trades:")
    for t in res['trades'][-10:]:
        ttime = t['time'].strftime("%Y-%m-%d %H:%M")
        if t['type'] == "BUY":
            print(f"  {ttime}  BUY  price={t['price']:.2f}  position={t['position']:.8f}  cash=${t['balance']:.2f}")
        else:
            print(f"  {ttime}  SELL price={t['price']:.2f}  pnl=${t.get('pnl',0):.2f}  cash=${t['balance']:.2f}")
    print("======================================================")

def run_once():
    df = fetch_klines()
    res = simulate_trading(df)
    pretty_print_result(res)

if __name__ == "__main__":
    if SLEEP_SECONDS <= 0:
        run_once()
    else:
        while True:
            try:
                run_once()
            except Exception as e:
                print("Error:", e)
            time.sleep(SLEEP_SECONDS)
