import pickle

import pandas as pd

if __name__ == '__main__':
    with open("./../../data/companies.pickle", "rb") as f:
        parse_names = pickle.load(f)
    sum_percents = 0
    count_percents = 0
    for t in parse_names:
        df = pd.read_csv(f"./../../data/parsed_{t['ticker']}.csv")
        df.dropna(inplace=True)
        df.drop(
            columns=["Unnamed: 0", "sent_score", "log_return", "volume", "overnight_variation", "trading_day_variation",
                     "word_count", "time"], inplace=True)
        # df["ma"] = df["close"].mul(df['close']).cumsum().div(df['close'].cumsum())
        df_copy = df.copy()
        a = df_copy.rolling(window=50, on="close").mean()
        df["ma"] = a["next_closing_price"]
        df.dropna(inplace=True)
        df_dict = df.to_dict(orient='rows')
        sign = -1
        for d in df_dict:
            d["prediction"] = 0
            if sign == -1 and d["ma"] > d["close"]:
                sign = 1
                d["prediction"] = 1
            elif sign == 1 and d["ma"] < d["close"]:
                sign = -1
                d["prediction"] = -1
        df = pd.DataFrame(df_dict)
        df_subset = df[df["prediction"] != 0]
        df_subset["prediction"] = df_subset["prediction"].map({1: True, -1: False})
        df_subset["actual"] = df_subset["next_closing_price"] > df_subset["close"]
        df_subset["true"] = df_subset["prediction"] == df_subset["actual"]
        # print(df_subset.head())
        ma_percent = df_subset["true"].sum() / df_subset["true"].count() * 100
        sum_percents += ma_percent
        count_percents += 1
        t["ma_parcent"] = ma_percent
        print(ma_percent)
    print("MEAN:", sum_percents / count_percents)
    for t in parse_names:
        t["mean_ma_percent"] = sum_percents / count_percents
    # print(parse_names)
    with open("./../../data/companies.pickle", "wb") as f:
        pickle.dump(parse_names, f)
