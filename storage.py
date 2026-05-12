import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
STATE_DIR = Path("state")

DATA_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

def append_csv(path, row):

    df = pd.DataFrame([row])

    if path.exists():
        df.to_csv(
            path,
            mode="a",
            header=False,
            index=False
        )
    else:
        df.to_csv(path, index=False)

def save_trade(coin, trade):

    path = DATA_DIR / f"{coin}_trades.csv"

    append_csv(path, trade)

def save_position(coin, position):

    path = DATA_DIR / f"{coin}_position.csv"

    pd.DataFrame([position]).to_csv(
        path,
        index=False
    )

def clear_position(coin):

    path = DATA_DIR / f"{coin}_position.csv"

    if path.exists():
        path.unlink()

def save_portfolio(snapshot):

    path = DATA_DIR / "portfolio.csv"

    append_csv(path, snapshot)

def save_state(coin, state_data):

    path = STATE_DIR / f"{coin}_state.json"

    with open(path, "w") as f:
        json.dump(state_data, f, indent=4)

def load_state(coin):

    path = STATE_DIR / f"{coin}_state.json"

    if not path.exists():
        return None

    with open(path, "r") as f:
        return json.load(f)
