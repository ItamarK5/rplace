from ..extensions import db
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, SmallInteger, Column

class Pixel(db.Model):
    __tablename__ = 'pixels'

<<<<<<< HEAD
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    drawer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    color = Column(SmallInteger())
    x = Column(SmallInteger())
    y = Column(SmallInteger())
    drawn = Column(db.Float, nullable=False)

=======
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    drawer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    color = db.Column(db.SmallInteger)
    x = db.Column(db.SmallInteger)
    y = db.Column(db.SmallInteger)
    drawn = db.Column(db.Float, nullable=False)
    
>>>>>>> parent of 300245e... 2.4.2
    def get_time(self) -> datetime:
        return datetime.fromtimestamp(self.draw_time)

    def set_time(self, tm: datetime) -> None:
        self.draw_time = tm.timestamp(tm)

