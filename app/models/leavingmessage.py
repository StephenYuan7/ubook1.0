from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship

from app.libs.error_code import NotFound
from app.models.base import Base, db


class Message(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    content = Column(String(500), nullable=False)
    image1 = Column(String(100))
    image2 = Column(String(100))
    image3 = Column(String(100))
    kind = Column(SmallInteger, default=0)
    hidden = Column(SmallInteger, default=0)
    hot = Column(SmallInteger, default=0)
    comment_num = Column(SmallInteger, default=0)

    message_relate_star = relationship("MessageStar", backref='star_relate_message')
    message_relate_comment = relationship("MessageComment", backref='comment_relate_message')

    def __init__(self):
        if self.create_time is None:
            super(Message, self).__init__()

    def keys(self):
        return ['id', 'user_id', 'content', 'create_datetime',
                'image1', 'image2', 'image3', 'kind',
                'hidden', 'hot', 'comment_num']

    @staticmethod
    def add_message(user_id, content, kind, hidden):
        with db.auto_commit():
            message = Message()
            message.user_id = user_id
            message.content = content
            message.kind = kind
            message.hidden = hidden

            db.session.add(message)
        return {"id":message.id}


class MessageStar(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, ForeignKey("message.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)

    def keys(self):
        return ['id', 'user_id', 'message_id', 'create_datetime']

    @staticmethod
    def add_star(user_id, message_id):
        message = Message.query.filter_by(id=message_id).first_or_404()
        message_star = MessageStar.query.\
            filter(MessageStar.message_id == message_id,MessageStar.user_id == user_id)\
            .first()
        if message_star:
            with db.auto_commit():
                if message_star.status == 0:
                    message_star.status = 1
                    message.hot = message.hot + 1
        else:
            with db.auto_commit():
                message_star = MessageStar()
                message_star.user_id = user_id
                message_star.message_id = message_id

                db.session.add(message_star)
            with db.auto_commit():
                if message_star.id:
                    message.hot = message.hot + 1
        return {"id": message_star.id}


class MessageComment(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, ForeignKey("message.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    content = Column(String(500), nullable=False)
    parent = Column(Integer, ForeignKey("message_comment.id"))

    comment_son = relationship("MessageComment", backref=db.backref(
                    'comment_parent',
                    remote_side=[id],
                    ),)

    def keys(self):
        return ['id', 'user_id', 'message_id', 'create_datetime', 'content'
                , 'parent']

    @staticmethod
    def add_comment(user_id, message_id, content, parent):

        with db.auto_commit():
            message_comment = MessageComment()
            message_comment.user_id = user_id
            message_comment.content = content
            message_comment.message_id = message_id
            if parent:
                message_comment.parent = parent
                parent_comment = MessageComment.query.filter_by(id=parent).first_or_404()
                if parent_comment.message_id != message_id:
                    raise NotFound()
            db.session.add(message_comment)
        with db.auto_commit():
            if message_comment.id:
                message = Message.query.filter_by(id=message_id).first_or_404()
                message.comment_num = message.comment_num + 1
        return {"id": message_comment.id}
