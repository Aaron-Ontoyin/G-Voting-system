
from sqlalchemy import Column, Integer, String, DateTime, Text, func, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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
        except IntegrityError:
            session.rollback()
            return False, "You already voted!"


engine = create_engine('postgresql://postgres:postgres@localhost:5432/g_voting')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()