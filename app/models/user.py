from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.error_code import AuthFailed, NotFound
from app.models.base import Base, db


class User(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    openid = Column(String(32), nullable=False)
    profile = Column(String(100), default='default.jpg')
    real_name = Column(String(50), nullable=False)
    user_academy = Column(String(30), nullable=False)
    nickname = Column(String(30), nullable=False)
    school_id = Column(Integer, ForeignKey("school.id"))
    user_grade = Column(String(7), nullable=False)
    student_number = Column(String(10), nullable=False)
    credibility = Column(SmallInteger, nullable=False, default=100)
    auth = Column(SmallInteger, default=1)
    qq = Column(Integer, nullable=False)

    user_relate_transaction = relationship("Transaction", backref='transaction_relate_user')
    user_relate_product = relationship("Product", backref='product_relate_user')
    user_relate_message = relationship("Message", backref='message_relate_user')
    user_relate_interest = relationship("Interest", backref='interest_relate_user')
    # user_relate_focuson1 = relationship("Focuson", backref='focuson1_relate_user',foreign_keys='focuson.user1_id')
    # user_relate_focuson2 = relationship("Focuson", backref='focuson2_relate_user',foreign_keys='focuson.user2_id')
    # user_relate_commit1 = relationship("Commit", backref='commit1_relate_user')
    # user_relate_commit2 = relationship("Commit", backref='commit2_relate_user')
    # user_relate_chattingrecord1 = relationship("Chattingrecord", backref='chattingrecord1_relate_user')
    # user_relate_chattingrecord2 = relationship("Chattingrecord", backref='chattingrecord2_relate_user')
    user_relate_attention = relationship("Attention", backref='attention_relate_user')
    user_relate_activity = relationship("Activity", backref='activity_relate_user')
    user_relate_message_star = relationship("MessageStar", backref='message_star_relate_user')
    user_relate_message_comment = relationship("MessageComment", backref='message_comment_relate_user')

    def __init__(self):
        if self.create_time is None:
            super(User, self).__init__()

    def keys(self):
        return ['id', 'profile', 'real_name', 'user_academy',
                'nickname', 'school_id', 'user_grade',
                'student_number', 'credibility', 'qq']

    @staticmethod
    def register_by_mina(openid, real_name, user_academy, nickname, school_id, user_grade, student_number, qq):
        with db.auto_commit():
            user = User()
            user.openid = openid
            user.real_name = real_name
            user.user_academy = user_academy
            user.nickname = nickname
            user.school_id = school_id
            user.user_grade = user_grade
            user.student_number = student_number
            user.qq = qq

            db.session.add(user)
