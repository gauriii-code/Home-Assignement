from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id = Column(Integer, primary_key=True)
    run_name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    config = Column(JSON)  # store strategy params e.g. short,long,stop,take
    metrics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trades = relationship("Trade", back_populates="run", cascade="all, delete-orphan")
    bars = relationship("Bar", back_populates="run", cascade="all, delete-orphan")

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"))
    timestamp = Column(DateTime, nullable=False)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    qty = Column(Integer)
    extra = Column(JSON)

    run = relationship("BacktestRun", back_populates="trades")

class Bar(Base):
    __tablename__ = "bars"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"))
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    run = relationship("BacktestRun", back_populates="bars")
