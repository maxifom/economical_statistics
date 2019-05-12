import pandas as pd
import matplotlib.pyplot as plt
from models import Company
import matplotlib.dates as mdates

if __name__ == '__main__':
    months = mdates.MonthLocator()
    monthFmt = mdates.DateFormatter('%Y-%m')
    companies = Company.select()
    for c in companies:
        df_linreg = pd.read_csv(f"./../../data/graph_data/linreg/{c.ticker}.csv")
        df_linreg = df_linreg[int(len(df_linreg) * 0.8):]
        df_linreg.reset_index(inplace=True)
        df_linreg.date = pd.to_datetime(df_linreg.date)

        df_arima = pd.read_csv(f"./../../data/graph_data/arima/{c.ticker}.csv")
        df_arima.date = pd.to_datetime(df_arima.date)

        fig, ax = plt.subplots(figsize=(12.8, 7.2))
        ax.plot(df_linreg.date, df_linreg.prediction, label="Prediction LinReg", color="green")
        ax.plot(df_linreg.date, df_arima.prediction, label="Prediction ARIMA", color="blue")
        ax.plot(df_linreg.date, df_arima.close, label="Actual", color="darkred", linestyle="--")
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthFmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        plt.xlabel("Date")
        plt.ylabel("Price, RUB")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/comparison/price/{c.ticker}.png", format="png")
        plt.clf()
        fig, ax = plt.subplots(figsize=(12.8, 7.2))
        ax.plot(df_linreg.date[5:], df_linreg.acc[5:], label="Test Accuracy LinReg", color="green")
        ax.plot(df_arima.date[5:], df_arima.acc[5:], label="Test Accuracy ARIMA", color="blue")
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthFmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        plt.xlabel("Date")
        plt.ylabel("Test Accuracy, %")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/comparison/acc/{c.ticker}.png", format="png")
        plt.clf()

        fig, ax = plt.subplots(figsize=(12.8, 7.2))
        ax.plot(df_linreg.date, df_linreg.val_loss, label="Test Value Loss LinReg", color="green")
        ax.plot(df_linreg.date, df_arima.val_loss, label="Test Value Loss ARIMA", color="blue")
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthFmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        plt.xlabel("Date")
        plt.ylabel("Test Value Loss")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/comparison/val_loss/{c.ticker}.png", format="png")
        plt.clf()

        fig, ax = plt.subplots(figsize=(12.8, 7.2))
        ax.plot(df_linreg.date, df_linreg.val_loss_pct, label="Test Value Loss % LinReg", color="green")
        ax.plot(df_arima.date, df_arima.val_loss_pct, label="Test Value Loss % ARIMA", color="blue")
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthFmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        plt.xlabel("Date")
        plt.ylabel("Test Value Loss, %")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/comparison/val_loss_pct/{c.ticker}.png", format="png")
        plt.clf()

        df_price = pd.DataFrame()
        df_price["arima"] = df_arima.prediction
        df_price["linreg"] = df_linreg.prediction
        df_price["date"] = df_linreg.date
        df_price["actual"] = df_arima.close
        df_price[["date", "arima", "linreg", "actual"]].to_csv(f"./../../data/graph_data/comparison/price_{c.ticker}.csv",
                                                     index=False)

        df_acc = pd.DataFrame()
        df_acc["arima"] = df_arima.acc[5:]
        df_acc["linreg"] = df_linreg.acc[5:]
        df_acc["date"] = df_linreg.date[5:]
        df_acc[["date", "arima", "linreg"]].to_csv(f"./../../data/graph_data/comparison/acc_{c.ticker}.csv",
                                                   index=False)

        df_val_loss = pd.DataFrame()
        df_val_loss["arima"] = df_arima.val_loss
        df_val_loss["linreg"] = df_linreg.val_loss
        df_val_loss["date"] = df_linreg.date
        df_val_loss[["date", "arima", "linreg"]].to_csv(f"./../../data/graph_data/comparison/val_loss_{c.ticker}.csv",
                                                        index=False)

        df_val_loss_pct = pd.DataFrame()
        df_val_loss_pct["arima"] = df_arima.val_loss_pct
        df_val_loss_pct["linreg"] = df_linreg.val_loss_pct
        df_val_loss_pct["date"] = df_linreg.date
        df_val_loss_pct[["date", "arima", "linreg"]].to_csv(
            f"./../../data/graph_data/comparison/val_loss_pct_{c.ticker}.csv",
            index=False)
