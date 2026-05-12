import streamlit as st
import pandas as pd
from pathlib import Path

from config import COINS

st.set_page_config(layout="wide")

st.title("Stateful Crypto Paper Trader")

data_dir = Path("data")
logs_dir = Path("logs")

st.subheader("Trades")

for coin in COINS:

    trade_file = data_dir / f"{coin}_trades.csv"

    if trade_file.exists():

        st.markdown(f"### {coin}")

        st.dataframe(
            pd.read_csv(trade_file),
            use_container_width=True
        )

portfolio_file = data_dir / "portfolio.csv"

if portfolio_file.exists():

    st.subheader("Portfolio History")

    st.dataframe(
        pd.read_csv(portfolio_file),
        use_container_width=True
    )

log_file = logs_dir / "system.log"

if log_file.exists():

    st.subheader("System Logs")

    with open(log_file, "r") as f:

        logs = f.read()

    st.text(logs[-10000:])
