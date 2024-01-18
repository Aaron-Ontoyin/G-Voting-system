import os

import dotenv

from sqlalchemy import Column, Integer, String, DateTime, Text, func, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


dotenv.load_dotenv()

Base = declarative_base()

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(String, unique=True)
    time = Column(DateTime(timezone=True), server_default=func.now())
    vote = Column(String)
    comment = Column(Text)

    __table_args__ = (
        UniqueConstraint('staff_id', name='uq_staff_id'),
    )

    @classmethod
    def insert_vote(cls, session, staff_id, vote, comment):
        try:
            new_vote = cls(staff_id=staff_id, vote=vote, comment=comment)
            session.add(new_vote)
            session.commit()
            return True, "Vote recorded successfully."
        except:
            session.rollback()
            return False, "You already voted!"

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
engine = create_engine(uri)

Base.metadata.create_all(engine)
