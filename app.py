import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

from config import COINS

st.set_page_config(
    layout="wide"
)

st.title(
    "Stateful Crypto Paper Trader"
)

# ==========================================================
# PATHS
# ==========================================================

data_dir = Path("data")

logs_dir = Path("logs")

# ==========================================================
# PORTFOLIO
# ==========================================================

portfolio_file = (
    data_dir / "portfolio.csv"
)

if portfolio_file.exists():

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    latest = portfolio_df.iloc[-1]

    st.subheader(
        "Portfolio Metrics"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Cash",
        f"${latest['Cash']:,.2f}"
    )

    col2.metric(
        "Equity",
        f"${latest['Equity']:,.2f}"
    )

    col3.metric(
        "Open Positions",
        int(latest["Open Positions"])
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Realized PnL",
        f"${latest['Realized PnL']:,.2f}"
    )

    col5.metric(
        "Unrealized PnL",
        f"${latest['Unrealized PnL']:,.2f}"
    )

    col6.metric(
        "Total Trades",
        int(latest["Total Trades"])
    )

    # ======================================================
    # EQUITY CURVE
    # ======================================================

    st.subheader(
        "Portfolio Equity Curve"
    )

    fig = px.line(
        portfolio_df,
        x="Timestamp",
        y="Equity"
    )

    st.plotly_chart(
        fig,
        width='stretch'
    )

    # ======================================================
    # PORTFOLIO TABLE
    # ======================================================

    st.subheader(
        "Portfolio History"
    )

    st.dataframe(
        portfolio_df.tail(50),
        width='stretch'
    )

# ==========================================================
# OPEN POSITIONS
# ==========================================================

st.subheader(
    "Open Positions"
)

positions_found = False

for coin in COINS:

    position_file = (
        data_dir / f"{coin}_position.csv"
    )

    if position_file.exists():

        positions_found = True

        st.markdown(f"### {coin}")

        pos_df = pd.read_csv(
            position_file
        )

        st.dataframe(
            pos_df,
            width='stretch'
        )

if not positions_found:

    st.info(
        "No open positions"
    )

# ==========================================================
# TRADE HISTORY
# ==========================================================

st.subheader(
    "Trade History"
)

for coin in COINS:

    trade_file = (
        data_dir / f"{coin}_trades.csv"
    )

    if trade_file.exists():

        st.markdown(f"### {coin}")

        trade_df = pd.read_csv(
            trade_file
        )

        st.dataframe(
            trade_df.tail(20),
            width='stretch'
        )

# ==========================================================
# LOGS
# ==========================================================

log_file = (
    logs_dir / "system.log"
)

if log_file.exists():

    st.subheader(
        "System Logs"
    )

    with open(log_file, "r") as f:

        logs = f.read()

    st.text(
        logs[-12000:]
    )