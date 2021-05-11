from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class Chattingrecord(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user1_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    user2_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    text = Column(String(500))
    type = Column(String(1))

    chattingrecord1_relate_user = relationship("User", backref='user_relate_chattingrecord1', foreign_keys=[user1_id])
    chattingrecord2_relate_user  = relationship("User", backref='user_relate_chattingrecord2', foreign_keys=[user2_id])

    def __init__(self):
        if self.create_time is None:
            super(Chattingrecord, self).__init__()

    def keys(self):
        return ['id', 'user1_id','user2_id','text','type', 'create_datetime']

    @staticmethod
    def up_by_mina(user1_id, user2_id, text, type):
        with db.auto_commit():
            chatting = Chattingrecord()
            chatting.user1_id = user1_id
            chatting.user2_id = user2_id
            chatting.text = text
            chatting.type = type
            db.session.add(chatting)
        return {"chatting_id": chatting.id}
