from sqlalchemy import Column, Integer, String, SmallInteger, Float, ForeignKey
from app.models.base import Base, db


class Attention(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"),nullable=False)

    def __init__(self):
        if self.create_time is None:
            super(Attention, self).__init__()

    def keys(self):
        return ['id', 'user_id','product_id']

    @staticmethod
    def up_by_mina(user_id, product_id):
        with db.auto_commit():
            attention = Attention()
            attention.user_id = user_id
            attention.product_id = product_id

            db.session.add(attention)
        return {"attention_id": attention.id}