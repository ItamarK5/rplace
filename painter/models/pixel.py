from ..extensions import db
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, SmallInteger, Column


class Pixel(db.Model):
    __tablename__ = 'pixels'

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    drawer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    color = Column(SmallInteger())
    x = Column(SmallInteger())
    y = Column(SmallInteger())
    drawn = Column(db.Float, nullable=False)

    def get_time(self) -> datetime:
        return datetime.fromtimestamp(self.draw_time)

    def set_time(self, tm: datetime) -> None:
        self.draw_time = tm.timestamp(tm)

