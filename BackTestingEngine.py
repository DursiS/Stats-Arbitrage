import matplotlib.pyplot as plt
from numpy import ndarray
import numpy as np
import yfinance as yf
from collections import deque

from Spread_Z_MReversion_Regime import (
    get_prices,
    get_price_spread,
    get_z_scores,
    visualize,
    get_returns,
    get_rolling_corr,
    get_signals,
    plot_signals,
)


class SpreadBacktestEngine:
    """A simple engine for running trading strategy backtests.

    Public Attributes:
        - prices: The history of prices which this asset has taken on.
        - cash: Liquid cash available, this may be negative
        - holdings: Number of total holdings
        - trades: A collection of the history of all holdings bought or sold.
                  Each tuple is in the format:
                  tuple[#holdings, "buy"/"sell", #day, price of holding]
    """

    tickers: tuple[str, str]
    prices: ndarray
    cash: float
    holdings: dict[str, list[tuple[int, int, float]]]

    def __init__(
        self, prices: ndarray, starting_cash: float, tickers: tuple[str, str]
    ) -> None:
        self.cash = starting_cash
        self.prices = prices
        self.holdings = {"own": [], "short": []}
        self.tickers = tickers

    def _cover_shorts_first(self, day: int, n: int) -> int:
        """Helper function to buy.

        Buy sold shares first before buying.

        Return how many shares are left to buy.
        """
        while self.holdings["short"] and n > 0:
            trade_i = self.holdings["short"][0]
            shares = trade_i[0]
            close_amount = min(shares, n)

            n -= close_amount
            self.cash -= close_amount * self.prices[day]

            if close_amount == shares:
                self.holdings["short"].pop(0)
            else:
                self.holdings["short"][0] = (
                    shares - close_amount,
                    trade_i[1],
                    trade_i[2],
                )

        return n

    def buy(self, day: int, n: int) -> None:
        """Buy <n> many shares on <day>.

        If shorted shares exist, cover them first.
        If shares remain, buy that position.

        Precondition: n > 0
        """
        n = self._cover_shorts_first(day, n)

        if n > 0:
            self.holdings["own"].append((n, day, self.prices[day]))
            self.cash -= n * self.prices[day]

    def _sell_owned_first(self, day: int, n: int) -> int:
        """Helper function to sell.

        Sell owned shares first before opening new shorts.

        Return how many shares are left to short.
        """
        while self.holdings["own"] and n > 0:
            trade_i = self.holdings["own"][0]
            shares = trade_i[0]
            close_amount = min(shares, n)

            n -= close_amount
            self.cash += close_amount * self.prices[day]

            if close_amount == shares:
                self.holdings["own"].pop(0)
            else:
                self.holdings["own"][0] = (
                    shares - close_amount,
                    trade_i[1],
                    trade_i[2],
                )
        return n

    def sell(self, day: int, n: int) -> None:
        """Sell <n> many shares on <day>.

        If owned shares exist, sell them first.
        If shares remain, open a short position.

        Precondition: n > 0
        """
        n = self._sell_owned_first(day, n)

        if n > 0:
            self.holdings["short"].append((n, day, self.prices[day]))
            self.cash += n * self.prices[day]

    def portfolio_value(self, day: int) -> float:
        """Return the net value this portfolio is worth on <day>."""

        total = self.cash

        if self.holdings["own"]:
            for trade in self.holdings["own"]:
                total += trade[0] * self.prices[day]
        else:
            for trade in self.holdings["short"]:
                total -= trade[0] * self.prices[day]

        return total

    def print_portfolio_returns(self, day: int) -> None:
        """Print the net value this portfolio is worth on <day>."""
        value = round(self.portfolio_value(day), 2)
        print(
            f"""
Portfolio Value: {value}$
Starting Cash: {STARTING_CASH}$
PNL: {round(value - STARTING_CASH, 2)}"""
        )

    def run_strategy(self) -> None:
        """Buy and Sell according the signals generating for 1 year."""

        signals = get_signals(self.tickers[0], self.tickers[1])
        for signal in signals:
            n = int((self.cash // 4) // self.prices[signal[0]])
            if signal[-1]:
                self.buy(int(signal[0]), n)
            else:
                self.sell(int(signal[0]), n)

    def daily_returns(self) -> list[float]:
        """Return the percent change in portfolio value between each day."""

    def total_return(self) -> float:
        """Return the overall per cent return from start to final day."""

    def max_drawdown(self) -> float:
        """Return the largest peak-to-trough portfolio loss."""

    def moving_average(self, day: int, window: int) -> float:
        """Return the average price over the last <window> days ending at <day>."""

    def run_moving_average_strategy(self, short_window: int, long_window: int) -> None:
        """Run a simple moving-average crossover strategy."""

    def reset(self) -> None:
        """Reset cash, holdings, and trades to the starting state."""

    def summary(self) -> None:
        """Print key backtest stats: final value, total return, trades, max drawdown."""
        print(f"Trades: {len(self.trades)}")


if __name__ == "__main__":

    SPREAD1 = get_price_spread("V", "MA")
    SPREAD2 = get_price_spread("PEP", "KO")
    STARTING_CASH = 5000.0
    TICKERS = ("V", "MA")

    sbe = SpreadBacktestEngine(SPREAD1, STARTING_CASH, TICKERS)
    sbe.run_strategy()
    sbe.print_portfolio_returns(len(SPREAD1))
