from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)

Base.metadata.create_all(engine)

def log_to_db(question, answer):
    session = Session()
    log = QueryLog(question=question, answer=answer)
    session.add(log)
    session.commit()
