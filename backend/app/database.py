from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]

if os.getenv("DATABASE_PATH"):
    DATABASE_PATH = Path(os.environ["DATABASE_PATH"])
elif os.name == "nt":
    DATABASE_PATH = BASE_DIR / "powercheck.db"
else:
    DATABASE_PATH = Path("/tmp/powercheck.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
