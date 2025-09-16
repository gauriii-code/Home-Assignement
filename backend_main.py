from fastapi import FastAPI, HTTPException
from db_access import SessionLocal
from sqlalchemy import select
from models import BacktestRun, Trade, Bar
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow local dev requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/runs")
def get_runs():
    session = SessionLocal()
    runs = session.query(BacktestRun).order_by(BacktestRun.created_at.desc()).all()
    out = []
    for r in runs:
        out.append({
            "id": r.id,
            "run_name": r.run_name,
            "symbol": r.symbol,
            "created_at": r.created_at.isoformat(),
            "metrics": r.metrics,
            "config": r.config
        })
    session.close()
    return out

@app.get("/runs/{run_id}/bars")
def get_bars(run_id: int):
    session = SessionLocal()
    bars = session.query(Bar).filter(Bar.run_id == run_id).order_by(Bar.timestamp).all()
    out = [{"timestamp": b.timestamp.isoformat(), "open": b.open, "high": b.high, "low": b.low, "close": b.close} for b in bars]
    session.close()
    return out

@app.get("/runs/{run_id}/trades")
def get_trades(run_id: int):
    session = SessionLocal()
    trades = session.query(Trade).filter(Trade.run_id == run_id).order_by(Trade.timestamp).all()
    out = [{"timestamp": t.timestamp.isoformat(), "symbol": t.symbol, "side": t.side, "price": t.price, "qty": t.qty} for t in trades]
    session.close()
    return out
