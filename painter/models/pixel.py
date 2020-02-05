from ..extensions import db
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, SmallInteger, Column

class Pixel(db.Model):
    __tablename__ = 'pixels'
    sqlite_autoincrement = True

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    drawer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    color = Column(SmallInteger())
    x = Column(SmallInteger())
    y = Column(SmallInteger())
    drawn = Column(db.Float, nullable=False)

    def get_time(self) -> datetime:
        return datetime.fromtimestamp(self.drawn)

    def set_time(self, tm: datetime) -> None:
        self.drawn = tm.timestamp(tm)

    def __repr__(self):
        return f"<Pixel(x={self.x},y={self.y},clr={self.color}>"
