from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from app.models.base import Base, db


class Transaction(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"),nullable=False)
    price = Column(SmallInteger, nullable=False, default=100)
    state = Column(String(1), nullable=False, default='0')
    address = Column(String(100))
    order_time = Column(Integer)
    over_time = Column(Integer)
    star = Column(Integer, default=5)
    evaluation = Column(String(1000))

    def __init__(self):
        if self.create_time is None:
            super(Transaction, self).__init__()

    def keys(self):
        return ['id', 'user_id','product_id','price',
                'state','address','order_time','over_time',
                'create_datetime']

    @staticmethod
    def up_by_mina(user_id, product_id, price, address, order_time):
        with db.auto_commit():
            transaction = Transaction()
            transaction.user_id = user_id
            transaction.product_id = product_id
            transaction.price = price
            transaction.address = address
            transaction.order_time = order_time
            transaction.over_time = transaction.create_time

            db.session.add(transaction)
        return {"transaction_id":transaction.id}
