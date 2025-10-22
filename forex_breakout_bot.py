"""
Forex Breakout Bot by Createev Tech
----------------------------------
This bot identifies potential breakout opportunities using MetaTrader-style logic.
It’s intended for simulation and educational testing only.
"""

import random
import time

def get_candle_data():
    """Simulate candle data for demo purposes."""
    price = 1.1000 + random.uniform(-0.005, 0.005)
    high = price + random.uniform(0.0005, 0.002)
    low = price - random.uniform(0.0005, 0.002)
    return {"open": price, "high": high, "low": low, "close": price}

def check_breakout(candle, resistance=1.1020, support=1.0980):
    """Detect breakout pattern from simulated data."""
    if candle["high"] > resistance:
        return "BREAKOUT ↑ (BUY SIGNAL)"
    elif candle["low"] < support:
        return "BREAKOUT ↓ (SELL SIGNAL)"
    else:
        return "NO BREAKOUT"

def run_bot():
    candle = get_candle_data()
    signal = check_breakout(candle)
    print(f"Price: {candle['close']:.5f} → {signal}")

if __name__ == "__main__":
    print("💹 Starting Forex Breakout Bot by Createev Tech")
    while True:
        run_bot()
        time.sleep(5)  # Runs every 5 seconds for demo
