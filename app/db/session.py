from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

POSTGRES_USER=settings.POSTGRES_USER
POSTGRES_PASSWORD=settings.POSTGRES_PASSWORD
POSTGRES_DB=settings.POSTGRES_DB
POSTGRES_HOST=settings.POSTGRES_HOST
POSTGRES_PORT=settings.POSTGRES_PORT

database_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

try:
    engine = create_engine(database_url)
except Exception as e:
    print(f"Failed to connect to DB, {str(e)}")
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database connection failed, {str(e)}")
        raise
    finally:
        db.close()