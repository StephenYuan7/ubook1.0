from sqlalchemy import Column, Integer, String, SmallInteger, Float, ForeignKey, orm
from sqlalchemy.orm import relationship

from app.models.base import Base, db


class Product(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    image1 = Column(String(100))
    image2 = Column(String(100))
    image3 = Column(String(100))
    title = Column(String(100), nullable=False)
    currentPrice = Column(Float)
    originalPrice = Column(Float)
    description = Column(String(1000))
    address = Column(String(100))
    kind = Column(SmallInteger)
    degree = Column(SmallInteger)
    state = Column(String(1))

    product_relate_transaction = relationship("Transaction", backref='transaction_relate_product')
    product_relate_attention = relationship("Attention", backref='attention_relate_product')

    @orm.reconstructor
    def __init__(self):
        if self.create_time is None:
            super(Product, self).__init__()
        self.fields = ['id', 'user_id', 'image1', 'image2',
                       'image3', 'title', 'currentPrice',
                       'originalPrice', 'description', 'address',
                       'kind', 'degree', 'state', 'create_datetime']

    def keys(self):
        """

        :return:
        """
        return self.fields

    @staticmethod
    def up_by_mina(title, currentPrice, originalPrice, description, address, kind, degree, state, user_id):
        """

        :param title:
        :param currentPrice:
        :param originalPrice:
        :param description:
        :param address:
        :param kind:
        :param degree:
        :param state:
        :param user_id:
        :return:
        """
        with db.auto_commit():
            product = Product()
            product.title = title
            product.currentPrice = currentPrice
            product.originalPrice = originalPrice
            product.description = description
            product.address = address
            product.kind = kind
            product.degree = degree
            product.state = state
            product.user_id = user_id

            db.session.add(product)
        return {"product_id": product.id}
