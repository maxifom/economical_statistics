if __name__ == '__main__':
    # import pickle
    #
    # lg = list()
    # with open('linreg.pickle', 'rb') as file:
    #     lg = pickle.load(file)
    # lg = list(filter(lambda l: l["next_price"] != -1, lg))
    # headers = ['sent_score', 'log_return', 'trading_volume', 'overnight_variation',
    #            'trading_day_variation', 'word_count', 'closing_price', 'next_price']
    # import csv
    #
    # with open('ligreg.csv', 'w', newline='') as csv_file:
    #     writer = csv.writer(csv_file)
    #     writer.writerow(headers)
    #     for l in lg:
    #         item = []
    #         for h in headers:
    #             item.append(l[h])
    #         writer.writerow(item)
    import pandas as pd

    df = pd.read_csv("ligreg.csv")
    # x - таблица с исходными данными факторов (x1, x2, x3)
    x = df.iloc[:, :-1]
    # y - таблица с исходными данными зависимой переменной
    y = df.iloc[:, -1]
    import statsmodels.api as sm

    x_ = sm.add_constant(x)
    smm = sm.OLS(y, x_)
    res = smm.fit()
    print(res.params)
    for r in res.params:
        print("{:10.8f}".format(r))
