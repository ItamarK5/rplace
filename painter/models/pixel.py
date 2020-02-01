from ..extensions import db
from datetime import datetime


class Pixel(db.Model):
    __tablename__ = 'pixels'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    drawer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    color = db.Column(db.SmallInteger)
    x = db.Column(db.SmallInteger)
    y = db.Column(db.SmallInteger)
    drawn = db.Column(db.Float, nullable=False)
    
    def get_time(self) -> datetime:
        return datetime.fromtimestamp(self.draw_time)

    def set_time(self, tm: datetime) -> None:
        self.draw_time = tm.timestamp(tm)

