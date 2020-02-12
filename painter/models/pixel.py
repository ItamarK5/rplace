from sqlalchemy import Integer, ForeignKey, SmallInteger, Column
from ..extensions import db


class Pixel(db.Model):
    __tablename__ = 'pixels'

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    drawer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    color = Column(SmallInteger())
    x = Column(SmallInteger())
    y = Column(SmallInteger())
    drawn = Column(db.Float, nullable=False)

