from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.business_term import Base

# Connection string:
# MySQL: "mysql+pymysql://user:password@localhost:3306/db_name"

DATABASE_URL = "mysql+pymysql://dict_user:dict_pass@localhost:3306/dict_db" # see docker-compose.yml

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Create all tables if not exist."""
    Base.metadata.create_all(bind=engine)

