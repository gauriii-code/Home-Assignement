"""
Lumibot SMA Crossover strategy with stop-loss (1%) and take-profit (50%).

Implements:
- Short SMA = 20
- Long SMA = 50
- Buy when short SMA crosses above long SMA
- Sell when short SMA crosses below long SMA
- Stop-loss: exit if unrealized loss >= 1% of position size
- Take-profit: exit when position profit >= 50%
"""

from lumibot.strategies.strategy import Strategy
from lumibot.traders.algorithmic_trader import AlgorithmicTrader
import pandas as pd
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

class SMACrossoverStrategy(Strategy):
    """
    Lumibot Strategy. Configure via params passed to init.
    """
    def __init__(self,
                 short_window: int = 20,
                 long_window: int = 50,
                 stop_loss_pct: float = 0.01,
                 take_profit_pct: float = 0.50,
                 symbol: str = "AAPL",
                 size: float = 10000.0,
                 timeframe: str = "1d"):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.symbol = symbol
        self.size = size
        self.timeframe = timeframe

        # runtime state
        self.in_position = False
        self.entry_price = None
        self.entry_qty = 0
        self.trades = []  # list of trade dicts for saving later

    def on_trading_iteration(self, timestamp, signal):
        # Lumibot pro: get historical bars via self.get_historical_prices or similar
        # Use price data; this is pseudocode depending on lumibot API.
        bars = self.data.get(self.symbol)  # depending on lumibot data feed
        if bars is None or len(bars) < self.long_window + 1:
            return

        close = pd.Series([bar.close for bar in bars])
        short_sma = close.rolling(self.short_window).mean()
        long_sma = close.rolling(self.long_window).mean()

        # compute cross
        if len(close) < 2:
            return

        prev_short = short_sma.iloc[-2]
        prev_long = long_sma.iloc[-2]
        cur_short = short_sma.iloc[-1]
        cur_long = long_sma.iloc[-1]
        last_price = float(close.iloc[-1])

        # cross-up: buy
        if (prev_short <= prev_long) and (cur_short > cur_long) and (not self.in_position):
            # determine qty to buy based on size and last_price
            qty = math.floor(self.size / last_price)
            if qty <= 0:
                logger.warning("Position size too small to buy any shares at price %s", last_price)
                return
            self.order_target_percent(self.symbol, 1.0)  # or market buy
            self.in_position = True
            self.entry_price = last_price
            self.entry_qty = qty
            self.trades.append({
                "timestamp": timestamp,
                "symbol": self.symbol,
                "side": "BUY",
                "price": last_price,
                "qty": qty
            })
            logger.info("BUY %s %d @ %s", self.symbol, qty, last_price)

        # cross-down: sell
        elif (prev_short >= prev_long) and (cur_short < cur_long) and self.in_position:
            self.order_target_percent(self.symbol, 0.0)  # close
            self.in_position = False
            exit_price = last_price
            self.trades.append({
                "timestamp": timestamp,
                "symbol": self.symbol,
                "side": "SELL",
                "price": exit_price,
                "qty": self.entry_qty
            })
            logger.info("SELL %s %d @ %s", self.symbol, self.entry_qty, exit_price)
            self.entry_price = None
            self.entry_qty = 0

        # risk management (stop-loss / take-profit)
        elif self.in_position:
            # compute P&L
            unrealized = (last_price - self.entry_price) / self.entry_price
            if unrealized <= -self.stop_loss_pct:
                # stop loss triggered
                self.order_target_percent(self.symbol, 0.0)
                self.in_position = False
                self.trades.append({
                    "timestamp": timestamp,
                    "symbol": self.symbol,
                    "side": "SELL_STOPLOSS",
                    "price": last_price,
                    "qty": self.entry_qty
                })
                logger.info("STOP LOSS SELL %s %d @ %s (unrealized %.4f)", self.symbol, self.entry_qty, last_price, unrealized)
                self.entry_price = None
                self.entry_qty = 0
            elif unrealized >= self.take_profit_pct:
                # take profit triggered
                self.order_target_percent(self.symbol, 0.0)
                self.in_position = False
                self.trades.append({
                    "timestamp": timestamp,
                    "symbol": self.symbol,
                    "side": "SELL_TAKEPROFIT",
                    "price": last_price,
                    "qty": self.entry_qty
                })
                logger.info("TAKE PROFIT SELL %s %d @ %s (unrealized %.4f)", self.symbol, self.entry_qty, last_price, unrealized)
                self.entry_price = None
                self.entry_qty = 0
