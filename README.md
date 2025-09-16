# Home-Assignement
# Lumibot SMA Crossover — Assignment Submission

## Summary
This repository contains a complete implementation of a short-term (20 SMA) / long-term (50 SMA) moving average crossover strategy using Lumibot / pandas, with:
- buy / sell signals on crossovers,
- stop-loss (1% from entry),
- take-profit / book-profit (50%),
- storage of results in PostgreSQL and CSV,
- a FastAPI backend to serve results,
- a React frontend using `lightweight-charts` to visualize price and trade markers.

---

## Files & Structure
(see file tree in repo root)

---

## Strategy Description
- **Indicators**: 20-day SMA and 50-day SMA on daily close.
- **Entry**: Buy when 20-SMA crosses above 50-SMA.
- **Exit**:
  - Sell when 20-SMA crosses below 50-SMA.
  - Stop-loss: exit if trade unrealized loss reaches 1% of entry price.
  - Take-profit: exit if trade unrealized profit reaches 50% of entry price.
- **Position sizing**: Uses `size` (USD) variable; quantity = floor(size / price).

---

## Backtesting
- Data: `yfinance` (daily bars used in `backtest_runner.py`).
- Two options:
  - Lumibot-native backtest (recommended), using `SMACrossoverStrategy`.
  - `simple_pandas_backtest` implemented for deterministic reproducibility without Lumibot.

### Metrics computed (see `metrics.py`):
- `total_return`
- `annualized_return` (approx)
- `max_drawdown`
- `sharpe_ratio` (assuming risk-free = 0)
- `number_of_trades`

---

## Database schema & motivation
Tables:
- `backtest_runs` (id, run_name, symbol, start_time, end_time, config JSON, metrics JSON)
- `trades` (id, run_id FK, timestamp, symbol, side, price, qty, extra JSON)
- `bars` (id, run_id FK, timestamp, open, high, low, close, volume)

**Rationale**:
- `backtest_runs` acts as an anchor for each experiment and stores config & metrics in JSON for flexible querying.
- `trades` stores the exact trade events needed to overlay on charts.
- `bars` stores the price timeseries for reproducible front-end displays without re-downloading.
- Not storing raw, monolithic backtest output; instead normalised so different runs are comparable.

---

## How to run (local)

### 1) Postgres
Create DB and set `DATABASE_URL`. Example:
```bash
# using psql
createdb lumibot_db
# or in docker:
docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
