import pandas as pd
import numpy as np
from math import sqrt

def compute_metrics(df, trades, initial_capital=10000.0):
    """
    Compute simple metrics:
      - total_return
      - annualized return (approx)
      - max drawdown
      - sharpe ratio (using daily returns)
      - number_of_trades
    """
    # Build equity curve from trades applied to initial capital
    # Simplified: assume all capital used per trade size provided in backtest runner
    # For pandas backtest, use per-trade results to compute returns.

    # Create a series of portfolio value timestamps using close prices
    close = df['close'].copy()
    # apply trades to compute equity series:
    positions = pd.Series(0, index=close.index, dtype=float)
    cash = pd.Series(initial_capital, index=close.index, dtype=float)

    current_qty = 0
    for t in trades:
        ts = t['timestamp']
        # align to index
        if ts not in positions.index:
            # find nearest timestamp
            ts = positions.index[positions.index.get_indexer([ts], method='nearest')[0]]
        side = t['side']
        price = t['price']
        qty = t['qty']
        idx = positions.index.get_loc(ts)
        if side.startswith("BUY"):
            current_qty += qty
            cash.iloc[idx:] -= qty * price
        else:
            current_qty -= qty
            cash.iloc[idx:] += qty * price
        positions.iloc[idx:] = current_qty

    portfolio = cash + positions * close
    portfolio = portfolio.fillna(method='ffill').fillna(initial_capital)

    returns = portfolio.pct_change().dropna()
    total_return = (portfolio.iloc[-1] / initial_capital) - 1.0

    # annualized return approximation
    days = (portfolio.index[-1] - portfolio.index[0]).days
    annual_return = (1 + total_return) ** (365.0 / days) - 1 if days > 0 else np.nan

    # max drawdown
    running_max = portfolio.cummax()
    drawdown = (portfolio - running_max) / running_max
    max_drawdown = drawdown.min()

    # sharpe ratio (assume risk-free ~0)
    if returns.std() != 0:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)  # daily returns
    else:
        sharpe = np.nan

    metrics = {
        "initial_capital": initial_capital,
        "final_portfolio_value": float(portfolio.iloc[-1]),
        "total_return": float(total_return),
        "annualized_return": float(annual_return),
        "max_drawdown": float(max_drawdown),
        "sharpe_ratio": float(sharpe) if not np.isnan(sharpe) else None,
        "number_of_trades": len(trades),
    }
    return metrics
