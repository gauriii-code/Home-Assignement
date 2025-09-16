import os
import pandas as pd
import numpy as np
import yfinance as yf
import logging
from datetime import datetime
from lumibot.backtesting import Backtest  # pseudocode: actual import depends on lumibot version
from lumibot.exchange.sandbox import SandboxExchange  # example
from lumibot.brokers.paper_broker import PaperBroker
from lumibot.traders import BacktestingTrader  # adjust to version
from lumibot_strategy import SMACrossoverStrategy
from metrics import compute_metrics
from save_results import save_results_to_db, save_results_to_csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_price_data(symbol: str, interval: str = "1d", period: str = "2y"):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    df = df.dropna()
    df.index = pd.to_datetime(df.index)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    return df

def run_backtest(symbol="AAPL",
                 short=20, long=50,
                 stop_loss=0.01, take_profit=0.5,
                 size=10000.0,
                 start=None, end=None,
                 interval="1d"):
    # Download data
    logger.info("Downloading data for %s", symbol)
    df = download_price_data(symbol, interval=interval, period="2y")

    # Option A: Use Lumibot Backtest API (pseudocode)
    # Build exchange / data feed objects as required by your lumibot version.
    # Trader, strategy wiring depends on version.
    strategy = SMACrossoverStrategy(short_window=short,
                                    long_window=long,
                                    stop_loss_pct=stop_loss,
                                    take_profit_pct=take_profit,
                                    symbol=symbol,
                                    size=size,
                                    timeframe=interval)

    # If Lumibot backtest runner is not available, run a simple pandas backtest below:
    trades = simple_pandas_backtest(df, short, long, stop_loss, take_profit, size, symbol)

    # compute metrics
    metrics = compute_metrics(df, trades, initial_capital=size)
    # Save results
    save_results_to_csv(symbol, trades, metrics)
    # Try to save to DB
    try:
        save_results_to_db(symbol, trades, metrics)
    except Exception as e:
        logger.warning("Could not save to DB: %s", e)

    return trades, metrics

def simple_pandas_backtest(df, short, long, stop_loss, take_profit, size, symbol):
    """
    A reproducible pandas-based backtest implementation for environments without Lumibot.
    Returns trade list (dicts).
    """
    close = df['close']
    short_sma = close.rolling(short).mean()
    long_sma = close.rolling(long).mean()

    in_pos = False
    entry_price = None
    entry_qty = 0
    trades = []

    for i in range(1, len(close)):
        if pd.isna(short_sma.iloc[i-1]) or pd.isna(long_sma.iloc[i-1]):
            continue
        prev_short = short_sma.iloc[i-1]
        prev_long = long_sma.iloc[i-1]
        cur_short = short_sma.iloc[i]
        cur_long = long_sma.iloc[i]
        price = close.iloc[i]

        # buy
        if (prev_short <= prev_long) and (cur_short > cur_long) and not in_pos:
            qty = int(size // price)
            if qty == 0:
                continue
            entry_price = price
            entry_qty = qty
            in_pos = True
            trades.append({"timestamp": df.index[i], "symbol": symbol, "side": "BUY", "price": price, "qty": qty})
        elif in_pos:
            unrealized = (price - entry_price) / entry_price
            # stop-loss
            if unrealized <= -stop_loss:
                trades.append({"timestamp": df.index[i], "symbol": symbol, "side": "SELL_STOPLOSS", "price": price, "qty": entry_qty})
                in_pos = False
                entry_price = None
                entry_qty = 0
            elif unrealized >= take_profit:
                trades.append({"timestamp": df.index[i], "symbol": symbol, "side": "SELL_TAKEPROFIT", "price": price, "qty": entry_qty})
                in_pos = False
                entry_price = None
                entry_qty = 0
            elif (prev_short >= prev_long) and (cur_short < cur_long):
                trades.append({"timestamp": df.index[i], "symbol": symbol, "side": "SELL", "price": price, "qty": entry_qty})
                in_pos = False
                entry_price = None
                entry_qty = 0
    return trades

if __name__ == "__main__":
    # Example run for AAPL
    symbols = ["AAPL", "MSFT", "TSLA"]
    for sym in symbols:
        trades, metrics = run_backtest(symbol=sym, short=20, long=50, stop_loss=0.01, take_profit=0.5, size=10000, interval="1d")
        print(f"Results for {sym}:")
        print(metrics)
