from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class School(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    school_id = Column(SmallInteger, nullable=False, default=10013)
    name = Column(String(100), nullable=False)

    school_relate_user = relationship("User", backref='user_relate_school')
    school_relate_schoolbook = relationship("Schoolbook", backref='schoolbook_relate_school')
    school_relate_activity = relationship("Activity", backref='activity_relate_school')

    def __init__(self):
        if self.create_time is None:
            super(School, self).__init__()

    def keys(self):
        return ['id', 'school_id','name']