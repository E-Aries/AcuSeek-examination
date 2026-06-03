from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

# Use sync SQLite URL
engine = create_engine(DATABASE_URL.replace("+aiosqlite", "").replace("asyncpg", "psycopg2"), echo=False)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
