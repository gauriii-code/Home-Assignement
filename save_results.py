import csv
import os
from datetime import datetime
from models import BacktestRun, Trade, Bar, Base
from db import engine, SessionLocal
import json

Base.metadata.create_all(bind=engine)

def save_results_to_db(symbol, trades, metrics, bars_df=None, config=None, run_name=None):
    session = SessionLocal()
    run = BacktestRun(
        run_name = run_name or f"{symbol}_{datetime.utcnow().isoformat()}",
        symbol = symbol,
        config = config or {},
        metrics = metrics
    )
    session.add(run)
    session.flush()  # get run.id
    # save trades
    for t in trades:
        trade = Trade(
            run_id = run.id,
            timestamp = t['timestamp'],
            symbol = t.get('symbol', symbol),
            side = t.get('side'),
            price = float(t.get('price')),
            qty = int(t.get('qty', 0)),
            extra = {k:v for k,v in t.items() if k not in ('timestamp','symbol','side','price','qty')}
        )
        session.add(trade)
    # save bars if provided
    if bars_df is not None:
        for idx, row in bars_df.iterrows():
            bar = Bar(
                run_id = run.id,
                timestamp = idx.to_pydatetime(),
                open = float(row['open']),
                high = float(row['high']),
                low = float(row['low']),
                close = float(row['close']),
                volume = float(row.get('volume', 0.0))
            )
            session.add(bar)
    session.commit()
    session.close()
    return run.id

def save_results_to_csv(symbol, trades, metrics, out_dir="results"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    metrics_file = os.path.join(out_dir, f"{symbol}_metrics_{ts}.json")
    trades_file = os.path.join(out_dir, f"{symbol}_trades_{ts}.csv")

    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    with open(trades_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp","symbol","side","price","qty"])
        writer.writeheader()
        for t in trades:
            writer.writerow({
                "timestamp": t['timestamp'],
                "symbol": t.get('symbol', symbol),
                "side": t.get('side'),
                "price": t.get('price'),
                "qty": t.get('qty')
            })
    return metrics_file, trades_file
