#Type code here

import pandas as pd
import numpy as np


# =========================
# Indicator Functions
# =========================

def cumulative_return(prices: pd.Series, window: int):
    return (prices.iloc[-1] / prices.iloc[-window] - 1) * 100


def rsi(prices: pd.Series, window: int = 14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series.iloc[-1]


# =========================
# Strategy Logic
# =========================

def symphony_strategy(data: dict):
    """
    data: dict of {symbol: pd.Series}
    returns: dict of final portfolio weights
    """

    portfolio = {}

    # -------------------------------------------------
    # TOP LEVEL: QQQ 5-day crash check
    # -------------------------------------------------

    if cumulative_return(data["QQQ"], 5) < -5.5:

        # =============================
        # VOLATILE MARKET BRANCH
        # =============================

        if rsi(data["UVXY"], 21) > 62:

            if rsi(data["UVXY"], 10) > 74:

                if rsi(data["UVXY"], 10) < 84:

                    if cumulative_return(data["UVXY"], 2) < 4.5:
                        # 100% FLOT
                        volatile = {"FLOT": 1.0}
                    else:
                        # 4 FLOT + 2 VXX (weight-equal duplication)
                        volatile = {
                            "FLOT": 4/6,
                            "VXX": 2/6
                        }

                else:
                    volatile = {"FLOT": 1.0}
            else:
                volatile = {"FLOT": 1.0}

        else:
            volatile = {"BIL": 1.0}

        # Apply weight-specified 0.2 sleeve
        for asset, weight in volatile.items():
            portfolio[asset] = portfolio.get(asset, 0) + weight * 0.2

        # Remaining 80% in BIL
        portfolio["BIL"] = portfolio.get("BIL", 0) + 0.8

    else:

        # =============================
        # CORE OR BIL BRANCH
        # =============================

        if cumulative_return(data["SPY"], 5) < -5.5:
            portfolio["BIL"] = 1.0

        else:

            # ---- CORE ----

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

    return normalize(portfolio)


# =========================
# Utility
# =========================

def normalize(weights: dict):
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}