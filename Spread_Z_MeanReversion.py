import matplotlib.pyplot as plt
from numpy import ndarray
from scipy.stats import norm

import math
import numpy as np
import yfinance as yf


def get_prices(ticker: str) -> ndarray:
    """Return the daily of <ticker> over the past year
    as the mid-point between open and close.

    Precondition: <ticker> is a valid Stock Ticker
    """
    tick = yf.Ticker(ticker)
    open = np.array([open for open in tick.history("1y")["Open"]])
    close = np.array([close for close in tick.history("1y")["Close"]])
    return (open + close) / 2


def get_price_spread(t1: str, t2: str) -> ndarray:
    """Return the difference in prices of <ticker1> and <ticker2>
    over the past year."""
    prices1 = get_prices(t1)
    prices2 = get_prices(t2)
    return np.abs(prices1 - prices2)


def get_z_scores(t1: str, t2: str) -> ndarray:
    """Return the rolling z scores between the spread of
    <ticker1> and <ticker2> within a year."""
    spread = get_price_spread(t1, t2)
    mean = spread.mean()
    std = spread.std()
    return np.array([(x - mean) / std for x in spread])


def visualize(t1: str, t2: str) -> None:
    """Plot Z-Score, mean and spread."""
    z = get_z_scores(t1, t2) * 100
    spread = get_price_spread(t1, t2)
    mean = np.ones(251) * spread.mean()
    day = [i for i in range(251)]

    plt.plot(day, spread, label="Spread ($)")
    plt.plot(day, z, label="Z Score * 100")
    plt.plot(day, mean, label="Spread Mean ($)")


def get_signals(t1: str, t2: str) -> list[tuple[float, float]]:
    """Signal to buy when Z >= 2, sell when Z <= 2.
    Return a list of tuple[day, spread, signal for...] for each large Z.
    True means Buy, False means Sell.
    """
    z = get_z_scores(t1, t2)
    spread = get_price_spread(t1, t2)
    day = [i for i in range(251)]

    signals = []
    for i in range(len(z)):
        if z[i] >= 2:
            signals.append((day[i], spread[i], True))
        if z[i] <= -2:
            signals.append((day[i], spread[i], False))
    return signals


def plot_signals(t1: str, t2: str) -> None:
    """Plot the points signalling to buy or sell."""
    signals = get_signals(t1, t2)

    buy = [(point[0], point[1]) for point in signals if point[2]]
    sell = [(point[0], point[1]) for point in signals if not point[2]]

    buy_days = [point[0] for point in buy]
    buy_vals = [point[1] for point in buy]

    sell_days = [point[0] for point in sell]
    sell_vals = [point[1] for point in sell]

    plt.scatter(buy_days, buy_vals, c="green", label="Buy Signal")
    plt.scatter(sell_days, sell_vals, c="red", label="Sell Signal")


if __name__ == "__main__":
    t1, t2 = "PEP", "KO"
    visualize(t1, t2)
    plot_signals(t1, t2)
    plt.legend()
    plt.show()
