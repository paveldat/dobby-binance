from collections import defaultdict
from datetime import datetime, timedelta
from traceback import format_exc
from typing import Dict

from sqlitedict import SqliteDict

from .binance_api_manager import BinanceAPIManager
from .binance_stream_manager import BinanceOrder
from .config import Config
from .database import Database
from .logger import Logger
from .models import Coin, Pair
from .strategies import get_strategy

cache = SqliteDict("data/backtest_cache.db")


class MockBinanceManager(BinanceAPIManager):
    def __init__(
        self,
        config: Config,
        db: Database,
        logger: Logger,
        start_date: datetime = None,
        start_balances: Dict[str, float] = None,
    ):
        super().__init__(config, db, logger)
        self.config = config
        self.datetime = start_date or datetime(2021, 1, 1)
        self.balances = start_balances or {config.BRIDGE.symbol: 100}

    def setup_websockets(self):
        pass  # No websockets are needed for backtesting

    def increment(self, interval=1):
        self.datetime += timedelta(minutes=interval)

    def get_fee(self, origin_coin: Coin, target_coin: Coin, selling: bool):
        return 0.00075

    def get_ticker_price(self, ticker_symbol: str):
        """
        Get ticker price of a specific coin
        """
        target_date = self.datetime.strftime("%d %b %Y %H:%M:%S")
        key = f"{ticker_symbol} - {target_date}"
        val = cache.get(key, None)
        if val is None:
            end_date = self.datetime + timedelta(minutes=1000)
            if end_date > datetime.now():
                end_date = datetime.now()
            end_date = end_date.strftime("%d %b %Y %H:%M:%S")
            self.logger.info(f"Fetching prices for {ticker_symbol} between {self.datetime} and {end_date}")
            for result in self.binance_client.get_historical_klines(
                ticker_symbol, "1m", target_date, end_date, limit=1000
            ):
                date = datetime.utcfromtimestamp(result[0] / 1000).strftime("%d %b %Y %H:%M:%S")
                price = float(result[1])
                cache[f"{ticker_symbol} - {date}"] = price
            cache.commit()
            val = cache.get(key, None)
        return val

    def get_currency_balance(self, currency_symbol: str, force=False):
        """
        Get balance of a specific coin
        """
        return self.balances.get(currency_symbol, 0)

    def buy_alt(self, origin_coin: Coin, target_coin: Coin):
        origin_symbol = origin_coin.symbol
        target_symbol = target_coin.symbol

        target_balance = self.get_currency_balance(target_symbol)
        from_coin_price = self.get_ticker_price(origin_symbol + target_symbol)

        order_quantity = self._buy_quantity(origin_symbol, target_symbol, target_balance, from_coin_price)
        target_quantity = order_quantity * from_coin_price
        self.balances[target_symbol] -= target_quantity
        self.balances[origin_symbol] = self.balances.get(origin_symbol, 0) + order_quantity * (
            1 - self.get_fee(origin_coin, target_coin, False)
        )
        self.logger.info(
            f"Bought {origin_symbol}, balance now: {self.balances[origin_symbol]} - bridge: "
            f"{self.balances[target_symbol]}"
        )

        event = defaultdict(lambda: None, order_price=from_coin_price, cumulative_quote_asset_transacted_quantity=0)

        return BinanceOrder(event)

    def sell_alt(self, origin_coin: Coin, target_coin: Coin):
        origin_symbol = origin_coin.symbol
        target_symbol = target_coin.symbol

        origin_balance = self.get_currency_balance(origin_symbol)
        from_coin_price = self.get_ticker_price(origin_symbol + target_symbol)

        order_quantity = self._sell_quantity(origin_symbol, target_symbol, origin_balance)
        target_quantity = order_quantity * from_coin_price
        self.balances[target_symbol] = self.balances.get(target_symbol, 0) + target_quantity * (
            1 - self.get_fee(origin_coin, target_coin, True)
        )
        self.balances[origin_symbol] -= order_quantity
        self.logger.info(
            f"Sold {origin_symbol}, balance now: {self.balances[origin_symbol]} - bridge: "
            f"{self.balances[target_symbol]}"
        )
        return {"price": from_coin_price}

    def collate_coins(self, target_symbol: str):
        total = 0
        for coin, balance in self.balances.items():
            if coin == target_symbol:
                total += balance
                continue
            if coin == self.config.BRIDGE.symbol:
                price = self.get_ticker_price(target_symbol + coin)
                if price is None:
                    continue
                total += balance / price
            else:
                price = self.get_ticker_price(coin + target_symbol)
                if price is None:
                    continue
                total += price * balance
        return total


class MockDatabase(Database):
    def __init__(self, logger: Logger, config: Config):
        super().__init__(logger, config, "sqlite:///")

    def log_scout(self, pair: Pair, target_ratio: float, current_coin_price: float, other_coin_price: float):
        pass


def backtest(
    start_date: datetime = None,
    end_date: datetime = None,
    interval=1,
    yield_interval=100,
    start_balances: Dict[str, float] = None,
    starting_coin: str = None,
    config: Config = None,
):
    """

    :param config: Configuration object to use
    :param start_date: Date to  backtest from
    :param end_date: Date to backtest up to
    :param interval: Number of virtual minutes between each scout
    :param yield_interval: After how many intervals should the manager be yielded
    :param start_balances: A dictionary of initial coin values. Default: {BRIDGE: 100}
    :param starting_coin: The coin to start on. Default: first coin in coin list

    :return: The final coin balances
    """
    config = config or Config()
    logger = Logger("backtesting", enable_notifications=False)

    end_date = end_date or datetime.today()

    db = MockDatabase(logger, config)
    db.create_database()
    db.set_coins(config.SUPPORTED_COIN_LIST)
    manager = MockBinanceManager(config, db, logger, start_date, start_balances)

    starting_coin = db.get_coin(starting_coin or config.SUPPORTED_COIN_LIST[0])
    if manager.get_currency_balance(starting_coin.symbol) == 0:
        manager.buy_alt(starting_coin, config.BRIDGE)
    db.set_current_coin(starting_coin)

    strategy = get_strategy(config.STRATEGY)
    if strategy is None:
        logger.error("Invalid strategy name")
        return manager
    trader = strategy(manager, db, logger, config)
    trader.initialize()

    yield manager

    n = 1
    try:
        while manager.datetime < end_date:
            try:
                trader.scout()
            except Exception:  # pylint: disable=broad-except
                logger.warning(format_exc())
            manager.increment(interval)
            if n % yield_interval == 0:
                yield manager
            n += 1
    except KeyboardInterrupt:
        pass
    cache.close()
    return manager
