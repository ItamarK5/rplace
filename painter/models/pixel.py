from sqlalchemy import Integer, ForeignKey, SmallInteger, Column

from ..extensions import datastore


class Pixel(datastore.Model):
    __tablename__ = 'pixels'

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    drawer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    color = Column(SmallInteger())
    x = Column(SmallInteger())
    y = Column(SmallInteger())
    drawn = Column(datastore.Float, nullable=False)
