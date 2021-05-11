from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class Commit(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user1_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    user2_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    content = Column(String(100), nullable=False)
    type = Column(String(1), nullable=False)

    commit1_relate_user = relationship("User", backref='user_relate_commit1', foreign_keys=[user1_id])
    commit2_relate_user = relationship("User", backref='user_relate_commit2', foreign_keys=[user2_id])

    def __init__(self):
        if self.create_time is None:
            super(Commit, self).__init__()

    def keys(self):
        return ['id', 'user1_id','user2_id','content','type', 'create_datetime']
