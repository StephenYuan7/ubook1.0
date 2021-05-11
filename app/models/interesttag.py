from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class Interesttag(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String(20))

    interesttag_relate_interest = relationship("Interest", backref='interest_relate_interesttag')

    def __init__(self):
        if self.create_time is None:
            super(Interesttag, self).__init__()

    def keys(self):
        return ['id','content']
