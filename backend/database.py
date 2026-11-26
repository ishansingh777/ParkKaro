from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

db_url = settings.sqlalchemy_database_url
engine_kwargs = {"pool_pre_ping": True}
if db_url.startswith("postgresql"):
    # Keep per-process pool small to stay well below Supabase session pool_size (15)
    engine_kwargs.update({"pool_size": 2, "max_overflow": 4, "pool_recycle": 180})

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
