from sqlalchemy import Column, Integer, String, SmallInteger, Float, ForeignKey
from app.models.base import Base, db


class Interest(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    tag_id = Column(Integer, ForeignKey("interesttag.id"),nullable=False)

    def __init__(self):
        if self.create_time is None:
            super(Interest, self).__init__()

    def keys(self):
        return ['id', 'user_id','tag_id']

    @staticmethod
    def add_interest(user_id, tag_id):
        with db.auto_commit():
            interest = Interest()
            interest.user_id = user_id
            interest.tag_id = tag_id

            db.session.add(interest)