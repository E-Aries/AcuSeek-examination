from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

# Use sync SQLite URL
engine = create_engine(
    DATABASE_URL.replace("+aiosqlite", "").replace("asyncpg", "psycopg2"),
    echo=False,
    pool_size=10,
    max_overflow=20,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

# Enable WAL mode for SQLite for better concurrent performance
def _init_db():
    if "sqlite" in DATABASE_URL:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=-8000"))  # 8MB cache
            # 创建常用查询索引
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_questions_created ON questions(created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_operation_logs_time ON operation_logs(created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_exam_papers_status ON exam_papers(status)"))
            conn.commit()
_init_db()

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
