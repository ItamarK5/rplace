from ..extensions import db
from datetime import datetime


class Pixel(db.Model):
    __tablename__ = 'pixels'
    sqlite_autoincrement = True

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    drawer = db.Column(db.BigInteger(), db.ForeignKey('users.id'), nullable=False)
    color = db.Column(db.SmallInteger)
    x = db.Column(db.SmallInteger)
    y = db.Column(db.SmallInteger)
    drawn = db.Column(db.Float, nullable=False)

    def get_time(self) -> datetime:
        return datetime.fromtimestamp(self.drawn)

    def set_time(self, tm: datetime) -> None:
        self.drawn = tm.timestamp(tm)

    def __repr__(self):
        return f"<Pixel(x={self.x},y={self.y},clr={self.color}>"
