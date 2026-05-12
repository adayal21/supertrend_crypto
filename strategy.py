import pandas as pd
import numpy as np

def calculate_atr(df, period=10):

    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())

    ranges = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    )

    true_range = ranges.max(axis=1)

    return true_range.rolling(period).mean()

def supertrend(df, atr_period=10, factor=3.0):

    df = df.copy()

    df['ATR'] = calculate_atr(df, atr_period)

    hl2 = (df['High'] + df['Low']) / 2

    upperband = hl2 + (factor * df['ATR'])
    lowerband = hl2 - (factor * df['ATR'])

    final_upperband = [0.0] * len(df)
    final_lowerband = [0.0] * len(df)

    supertrend = [0.0] * len(df)
    direction = [1] * len(df)

    for i in range(1, len(df)):

        close = float(df['Close'].iloc[i])
        prev_close = float(df['Close'].iloc[i - 1])

        curr_upper = float(upperband.iloc[i])
        curr_lower = float(lowerband.iloc[i])

        prev_final_upper = final_upperband[i - 1]
        prev_final_lower = final_lowerband[i - 1]

        if (
            curr_upper < prev_final_upper
            or prev_close > prev_final_upper
        ):
            final_upperband[i] = curr_upper
        else:
            final_upperband[i] = prev_final_upper

        if (
            curr_lower > prev_final_lower
            or prev_close < prev_final_lower
        ):
            final_lowerband[i] = curr_lower
        else:
            final_lowerband[i] = prev_final_lower

        prev_supertrend = supertrend[i - 1]

        if prev_supertrend == prev_final_upper:

            if close <= final_upperband[i]:
                supertrend[i] = final_upperband[i]
                direction[i] = 1
            else:
                supertrend[i] = final_lowerband[i]
                direction[i] = -1

        else:

            if close >= final_lowerband[i]:
                supertrend[i] = final_lowerband[i]
                direction[i] = -1
            else:
                supertrend[i] = final_upperband[i]
                direction[i] = 1

    df['Supertrend'] = supertrend
    df['Direction'] = direction

    return df
