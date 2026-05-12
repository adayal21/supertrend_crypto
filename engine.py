import pandas as pd
import requests

from datetime import datetime

from logger import logger

from config import *
from strategy import supertrend
from storage import *

portfolio_capital = INITIAL_PORTFOLIO_CAPITAL


# ==========================================================
# FETCH DATA FROM COINBASE
# ==========================================================

def fetch_data(coin):

    logger.info(
        f"{coin} | Fetching latest candles from Coinbase"
    )

    try:

        symbol = coin.replace("-USD", "-USD")

        url = (
            f"https://api.exchange.coinbase.com/"
            f"products/{symbol}/candles"
        )

        params = {
            "granularity": 3600
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if not data or isinstance(data, dict):

            logger.error(
                f"{coin} | Empty Coinbase response"
            )

            return None

        df = pd.DataFrame(
            data,
            columns=[
                "Time",
                "Low",
                "High",
                "Open",
                "Close",
                "Volume"
            ]
        )

        df["Time"] = pd.to_datetime(
            df["Time"],
            unit="s"
        )

        df = df.sort_values("Time")

        df.set_index("Time", inplace=True)

        logger.info(
            f"{coin} | Coinbase candles fetched | "
            f"Rows={len(df)}"
        )

        return df

    except Exception as e:

        logger.error(
            f"{coin} | Coinbase fetch failed | "
            f"Error={e}"
        )

        return None


# ==========================================================
# PROCESS SINGLE COIN
# ==========================================================

def process_coin(coin):

    global portfolio_capital

    logger.info(
        "\n"
        "--------------------------------------------------\n"
        f"{coin} PROCESSING\n"
        "--------------------------------------------------"
    )

    try:

        # ==================================================
        # FETCH DATA
        # ==================================================

        df = fetch_data(coin)

        if df is None or len(df) < 20:

            logger.error(
                f"{coin} | Insufficient candle data"
            )

            return {
                "Coin": coin,
                "Status": "NO_DATA"
            }

        # ==================================================
        # STRATEGY
        # ==================================================

        df = supertrend(
            df,
            atr_period=ATR_PERIOD,
            factor=FACTOR
        )

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        latest_timestamp = str(df.index[-1])

        logger.info(
            f"{coin} | Latest Candle | "
            f"Time={df.index[-1]} | "
            f"O={latest['Open']} | "
            f"H={latest['High']} | "
            f"L={latest['Low']} | "
            f"C={latest['Close']}"
        )

        # ==================================================
        # RESTORE STATE
        # ==================================================

        state = load_state(coin)

        if state is not None:

            last_processed = state["last_timestamp"]

            if latest_timestamp == last_processed:

                logger.info(
                    f"{coin} | No new candle detected"
                )

                return {
                    "Coin": coin,
                    "Status": "NO_NEW_CANDLE"
                }

            position = state["position"]
            entry_price = state["entry_price"]
            quantity = state["quantity"]

            logger.info(
                f"{coin} | State restored | "
                f"Position={position} | "
                f"Entry={entry_price}"
            )

        else:

            position = None
            entry_price = 0
            quantity = 0

            logger.info(
                f"{coin} | Fresh state initialized"
            )

        # ==================================================
        # SIGNALS
        # ==================================================

        direction = latest["Direction"]
        prev_direction = previous["Direction"]

        turns_green = prev_direction > direction
        turns_red = prev_direction < direction

        logger.info(
            f"{coin} | "
            f"Prev Direction={prev_direction} | "
            f"Current Direction={direction}"
        )

        close_price = float(latest["Close"])

        signal_triggered = False

        # ==================================================
        # LONG ENTRY
        # ==================================================

        if turns_green and position is None:

            signal_triggered = True

            allocation = min(
                CAPITAL_PER_TRADE,
                portfolio_capital
            )

            quantity = allocation / close_price

            position = "LONG"

            entry_price = close_price

            portfolio_capital -= allocation

            logger.info(
                f"{coin} | LONG ENTRY | "
                f"Price={close_price} | "
                f"Qty={quantity} | "
                f"Capital Remaining={portfolio_capital}"
            )

            save_position(
                coin,
                {
                    "Coin": coin,
                    "Side": "LONG",
                    "Entry Price": entry_price,
                    "Quantity": quantity,
                    "Timestamp": latest_timestamp
                }
            )

        # ==================================================
        # SHORT ENTRY
        # ==================================================

        elif turns_red and position is None:

            signal_triggered = True

            allocation = min(
                CAPITAL_PER_TRADE,
                portfolio_capital
            )

            quantity = allocation / close_price

            position = "SHORT"

            entry_price = close_price

            portfolio_capital -= allocation

            logger.info(
                f"{coin} | SHORT ENTRY | "
                f"Price={close_price} | "
                f"Qty={quantity} | "
                f"Capital Remaining={portfolio_capital}"
            )

            save_position(
                coin,
                {
                    "Coin": coin,
                    "Side": "SHORT",
                    "Entry Price": entry_price,
                    "Quantity": quantity,
                    "Timestamp": latest_timestamp
                }
            )

        # ==================================================
        # CLOSE LONG
        # ==================================================

        elif turns_red and position == "LONG":

            signal_triggered = True

            pnl = (
                (close_price - entry_price)
                * quantity
            )

            portfolio_capital += (
                CAPITAL_PER_TRADE + pnl
            )

            logger.info(
                f"{coin} | LONG EXIT | "
                f"Exit={close_price} | "
                f"PnL={pnl} | "
                f"Portfolio={portfolio_capital}"
            )

            save_trade(
                coin,
                {
                    "Coin": coin,
                    "Side": "LONG",
                    "Entry Price": entry_price,
                    "Exit Price": close_price,
                    "Quantity": quantity,
                    "PnL": pnl,
                    "Exit Time": latest_timestamp
                }
            )

            clear_position(coin)

            position = None
            entry_price = 0
            quantity = 0

        # ==================================================
        # CLOSE SHORT
        # ==================================================

        elif turns_green and position == "SHORT":

            signal_triggered = True

            pnl = (
                (entry_price - close_price)
                * quantity
            )

            portfolio_capital += (
                CAPITAL_PER_TRADE + pnl
            )

            logger.info(
                f"{coin} | SHORT EXIT | "
                f"Exit={close_price} | "
                f"PnL={pnl} | "
                f"Portfolio={portfolio_capital}"
            )

            save_trade(
                coin,
                {
                    "Coin": coin,
                    "Side": "SHORT",
                    "Entry Price": entry_price,
                    "Exit Price": close_price,
                    "Quantity": quantity,
                    "PnL": pnl,
                    "Exit Time": latest_timestamp
                }
            )

            clear_position(coin)

            position = None
            entry_price = 0
            quantity = 0

        # ==================================================
        # NO SIGNAL
        # ==================================================

        if not signal_triggered:

            logger.info(
                f"{coin} | No signal generated"
            )

        # ==================================================
        # SAVE STATE
        # ==================================================

        save_state(
            coin,
            {
                "last_timestamp": latest_timestamp,
                "position": position,
                "entry_price": entry_price,
                "quantity": quantity,
                "direction": int(direction),
                "supertrend": float(latest["Supertrend"])
            }
        )

        logger.info(
            f"{coin} | State saved successfully"
        )

        return {
            "Coin": coin,
            "Position": position,
            "Portfolio Capital": round(
                portfolio_capital,
                2
            ),
            "Status": "SUCCESS"
        }

    except Exception as e:

        logger.error(
            f"{coin} | Processing failed | Error={e}"
        )

        return {
            "Coin": coin,
            "Status": "FAILED"
        }


# ==========================================================
# RUN ENTIRE PORTFOLIO
# ==========================================================

def run_portfolio():

    global portfolio_capital

    logger.info(
        "\n"
        "==================================================\n"
        "PORTFOLIO CYCLE STARTED\n"
        "=================================================="
    )

    results = []

    # ======================================================
    # PROCESS ALL COINS
    # ======================================================

    for coin in COINS:

        result = process_coin(coin)

        results.append(result)

    # ======================================================
    # PORTFOLIO ACCOUNTING
    # ======================================================

    cash = portfolio_capital

    unrealized_pnl = 0

    open_positions = 0

    realized_pnl = 0

    total_trades = 0

    # ======================================================
    # OPEN POSITION ACCOUNTING
    # ======================================================

    for coin in COINS:

        position_file = (
            DATA_DIR / f"{coin}_position.csv"
        )

        if position_file.exists():

            try:

                pos_df = pd.read_csv(position_file)

                if len(pos_df) > 0:

                    open_positions += 1

                    side = pos_df.iloc[0]["Side"]

                    entry_price = float(
                        pos_df.iloc[0]["Entry Price"]
                    )

                    quantity = float(
                        pos_df.iloc[0]["Quantity"]
                    )

                    latest_df = fetch_data(coin)

                    if latest_df is not None:

                        current_price = float(
                            latest_df.iloc[-1]["Close"]
                        )

                        if side == "LONG":

                            pnl = (
                                current_price
                                - entry_price
                            ) * quantity

                        else:

                            pnl = (
                                entry_price
                                - current_price
                            ) * quantity

                        unrealized_pnl += pnl

            except Exception as e:

                logger.error(
                    f"{coin} | Position accounting failed | {e}"
                )

    # ======================================================
    # TRADE ACCOUNTING
    # ======================================================

    for coin in COINS:

        trade_file = (
            DATA_DIR / f"{coin}_trades.csv"
        )

        if trade_file.exists():

            try:

                trade_df = pd.read_csv(trade_file)

                total_trades += len(trade_df)

                if "PnL" in trade_df.columns:

                    realized_pnl += (
                        trade_df["PnL"].sum()
                    )

            except Exception as e:

                logger.error(
                    f"{coin} | Trade accounting failed | {e}"
                )

    # ======================================================
    # FINAL EQUITY
    # ======================================================

    equity = (
        cash
        + unrealized_pnl
    )

    # ======================================================
    # SAVE PORTFOLIO ONLY ONCE
    # ======================================================

    save_portfolio(
        {
            "Timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "Cash": round(cash, 2),

            "Equity": round(equity, 2),

            "Open Positions": open_positions,

            "Realized PnL": round(
                realized_pnl,
                2
            ),

            "Unrealized PnL": round(
                unrealized_pnl,
                2
            ),

            "Total Trades": total_trades
        }
    )

    logger.info(
        "\n"
        "==================================================\n"
        "PORTFOLIO SUMMARY\n"
        f"Cash               = {cash}\n"
        f"Equity             = {equity}\n"
        f"Open Positions     = {open_positions}\n"
        f"Realized PnL       = {realized_pnl}\n"
        f"Unrealized PnL     = {unrealized_pnl}\n"
        f"Total Trades       = {total_trades}\n"
        "=================================================="
    )

    logger.info(
        "Portfolio cycle completed"
    )

    return pd.DataFrame(results)