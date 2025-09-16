from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lumibot_db")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
