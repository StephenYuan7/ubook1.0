from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from app.models.base import Base, db


class Schoolbook(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=False)
    grade = Column(String(7), nullable=False)
    academy = Column(String(30), nullable=False)
    school_id = Column(Integer, ForeignKey("school.id"),nullable=False)
    term = Column(String(50), nullable=False)

    def __init__(self):
        if self.create_time is None:
            super(Schoolbook, self).__init__()

    def keys(self):
        return ['id', 'name','grade','academy',
                'school_id','term']
