from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URl = "sqlite:///./data/securebank.db"
engine = create_engine(
    DATABASE_URl,
    connect_args={"check_same_thread": False}  
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    """
    Dependency function used in FastAPI routes.
    Opens a DB session, yields it, then closes it after the request.
    
    Usage in route:
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables in the database.
    Called once at app startup.
    """
    from models import Base  
    Base.metadata.create_all(bind=engine)
    print("[DB] All tables created successfully.")
