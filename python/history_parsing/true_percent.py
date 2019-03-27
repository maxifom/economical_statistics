import pickle

import pandas as pd


def calculate_percent_true():
    with open('./../../data/companies.pickle', 'rb') as f:
        tickers = pickle.load(f)
    max_ = 0
    min_ = 100
    result = dict()
    result["values"] = []
    for t in tickers:
        r = dict()
        df = pd.read_csv('./../../data/parsed_{0}.csv'.format(t["ticker"]))
        df_dict = df.to_dict(orient='rows')
        tr = 0
        fals = 0
        for d in df_dict:
            prediction = 0
            for name, coef in t["coef"].items():
                if name == 'const':
                    prediction += coef
                    continue
                prediction += d[name] * coef
            if (d["next_closing_price"] >= d["close"]) == (prediction >= d["close"]):
                tr += 1
            else:
                fals += 1
        # print(t["ticker"])
        # print(tr, fals, tr / (tr + fals))
        r["true"] = tr
        if "name" in t:
            r["ticker"] = t["name"]
        elif "parse_name" in t:
            r["ticker"] = t["parse_name"]
        r["false"] = fals
        r["percent"] = tr / (tr + fals)
        max_ = max(max_, tr / (tr + fals))
        min_ = min(min_, tr / (tr + fals))
        result["values"].append(r)
    result["max"] = max_
    result["min"] = min_
    with open('./../../data/result.pickle', 'wb') as file:
        pickle.dump(result, file)


if __name__ == '__main__':
    calculate_percent_true()
