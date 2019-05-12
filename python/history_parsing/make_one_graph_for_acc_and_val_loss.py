import pandas as pd

from models import Company

if __name__ == '__main__':
    companies = Company.select()
    for type in ["linreg", "arima"]:
        for datatype in ["acc", "val_loss_pct"]:
            df = pd.DataFrame()
            for c in companies:
                df1 = pd.read_csv(f"./../../data/graph_data/{type}/{datatype}_{c.ticker}.csv")
                if len(df) == 0:
                    df["date"] = df1.date
                df[c.ticker] = df1[datatype]
                if len(df1) < len(df):
                    df[c.ticker] = df[c.ticker].shift(len(df) - len(df1))
            df.fillna(0, inplace=True)
            df.to_csv(f"./../../data/graph_data/{type}/all_{datatype}.csv", index=False)
