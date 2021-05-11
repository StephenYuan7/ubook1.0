from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class Focuson(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user1_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    user2_id = Column(Integer, ForeignKey("user.id"),nullable=False)

    focuson1_relate_user = relationship("User", backref='user_relate_focuson1', foreign_keys=[user1_id])
    focuson2_relate_user = relationship("User", backref='user_relate_focuson2', foreign_keys=[user2_id])

    def __init__(self):
        if self.create_time is None:
            super(Focuson, self).__init__()

    def keys(self):
        return ['id', 'user1_id','user2_id']

    @staticmethod
    def up_by_mina(user1_id, user2_id):
        with db.auto_commit():
            focus = Focuson()
            focus.user1_id = user1_id
            focus.user2_id = user2_id
            db.session.add(focus)
        return {"focus_id": focus.id}
