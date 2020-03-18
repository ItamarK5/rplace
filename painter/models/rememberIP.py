from sqlalchemy import String, Float, Column
from sqlalchemy.dialects.sqlite import DATETIME
from ..extensions import datastore
import time


class RememberIPTableMixin(datastore.Model):
    seconds_expires: float
    key: Column(String, primary_key=True)
    expires: Column(Float,  nullable=False)

    @classmethod
    def has_expired(cls, key: str) -> bool:
        val = cls.query.get(key)
        if val.expires > time.time():
            pass
        elif val
