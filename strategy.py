#!/usr/bin/env python3
"""
Time-based strategy for scheduled execution — no user inputs, paper by default

Rules (US/Eastern):
- Before 10:00 AM ET  -> BUY  1 KO (market, DAY)
- After  10:00 AM ET  -> SELL 1 KO (market, DAY)
- Exactly 10:00 AM ET -> no action

Requires env vars:
  APCA_API_KEY_ID, APCA_API_SECRET_KEY
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# --- Configuration (no user inputs) ---
SYMBOL = "KO"
QTY = 1
TZ_ET = ZoneInfo("US/Eastern")

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

if not API_KEY or not API_SECRET:
    sys.exit("Missing API credentials. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY in your environment.")

# Always paper trading
client = TradingClient(API_KEY, API_SECRET, paper=True)

def market_is_open() -> bool:
    try:
        return bool(client.get_clock().is_open)
    except Exception as e:
        print(f"Could not read market clock: {e}")
        return False

def place(side: OrderSide):
    order = MarketOrderRequest(
        symbol=SYMBOL,
        qty=QTY,
        side=side,
        time_in_force=TimeInForce.DAY,  # market order -> market price
    )
    submitted = client.submit_order(order)
    print(f"{datetime.now(TZ_ET).isoformat()}  {side.name} {QTY} {SYMBOL}  order_id={submitted.id}")

def main():
    now_et = datetime.now(TZ_ET)
    ten_am = now_et.replace(hour=10, minute=0, second=0, microsecond=0).time()

    if not market_is_open():
        print(f"[{now_et}] Market is closed. No action.")
        return

    if now_et.time() < ten_am:
        print(f"[{now_et}] Before 10:00 AM ET -> BUY")
        place(OrderSide.BUY)
    elif now_et.time() > ten_am:
        print(f"[{now_et}] After 10:00 AM ET -> SELL")
        place(OrderSide.SELL)
    else:
        print(f"[{now_et}] Exactly 10:00 AM ET -> no action")

if __name__ == "__main__":
    main()