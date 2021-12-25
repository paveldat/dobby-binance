from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base
from .pair import Pair


class ScoutHistory(Base):
    __tablename__ = "scout_history"

    id = Column(Integer, primary_key=True)

    pair_id = Column(String, ForeignKey("pairs.id"))
    pair = relationship("Pair")

    target_ratio = Column(Float)
    current_coin_price = Column(Float)
    other_coin_price = Column(Float)

    datetime = Column(DateTime)

    def __init__(
        self,
        pair: Pair,
        target_ratio: float,
        current_coin_price: float,
        other_coin_price: float,
    ):
        self.pair = pair
        self.target_ratio = target_ratio
        self.current_coin_price = current_coin_price
        self.other_coin_price = other_coin_price
        self.datetime = datetime.utcnow()

    @hybrid_property
    def current_ratio(self):
        return self.current_coin_price / self.other_coin_price

    def info(self):
        return {
            "from_coin": self.pair.from_coin.info(),
            "to_coin": self.pair.to_coin.info(),
            "current_ratio": self.current_ratio,
            "target_ratio": self.target_ratio,
            "current_coin_price": self.current_coin_price,
            "other_coin_price": self.other_coin_price,
            "datetime": self.datetime.isoformat(),
        }
