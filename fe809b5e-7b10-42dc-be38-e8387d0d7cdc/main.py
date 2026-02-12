#Type c
import pandas as pd
import numpy as np

# --- Indicators ---

def cumulative_return(prices: pd.Series, window: int):
    return (prices.iloc[-1] / prices.iloc[-window] - 1) * 100


def rsi(prices: pd.Series, window: int = 14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]


# --- Strategy Logic ---

def symphony_strategy(data):
    """
    data: dict of {symbol: pd.Series of prices}
    returns: dict of {symbol: weight}
    """

    portfolio = {}

    # Top-level condition
    if cumulative_return(data["QQQ"], 5) < -5.5:

        # ---- Volatile Market Branch ----
        if rsi(data["UVXY"], 21) > 62:

            if rsi(data["UVXY"], 10) > 74:

                if rsi(data["UVXY"], 10) < 84:

                    if cumulative_return(data["UVXY"], 2) < 4.5:
                        volatile_allocation = {"FLOT": 1.0}
                    else:
                        volatile_allocation = {
                            "FLOT": 4/6,
                            "VXX": 2/6
                        }

                else:
                    volatile_allocation = {"FLOT": 1.0}
            else:
                volatile_allocation = {"FLOT": 1.0}

        else:
            volatile_allocation = {"BIL": 1.0}

        # Apply 20% to volatile sleeve
        for k, v in volatile_allocation.items():
            portfolio[k] = portfolio.get(k, 0) + v * 0.2

        # 80% BIL
        portfolio["BIL"] = portfolio.get("BIL", 0) + 0.8

    else:

        # ---- Core or BIL Branch ----
        if cumulative_return(data["SPY"], 5) < -5.5:
            portfolio["BIL"] = 1.0

        else:

            if rsi(data["TQQQ"], 10) > 79:
                portfolio["UVXY"] = 1.0

            elif rsi(data["SPXL"], 10) > 80:
                portfolio["UVXY"] = 1.0

            elif rsi(data["QQQ"], 10) < 31:
                portfolio["TQQQ"] = 0.5
                portfolio["TECL"] = 0.5

            else:
                portfolio["GLD"] = 1/3
                portfolio["SHY"] = 1/3
                portfolio["UUP"] = 1/3

    return portfolio