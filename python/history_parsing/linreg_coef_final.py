import pickle

import statsmodels.api as sm
import pandas as pd


def calculate_percent_true():
    with open('./../../data/companies.pickle', 'rb') as f:
        tickers = pickle.load(f)
    max_ = 0
    min_ = 100
    for t in tickers:
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
        print(t["ticker"])
        print(tr, fals, tr / (tr + fals))
        max_ = max(max_, tr / (tr + fals))
        min_ = min(min_, tr / (tr + fals))
    print(max_, min_)


def calculate_linreg_coef_and_pvalues():
    tickers = [{'name': 'Safmar Fin', 'ticker': 'SFIN', 'parse_name': 'Сафмар, Safmar'},
               {'name': 'X5 Retail Group', 'ticker': 'FIVE', 'parse_name': 'X5'},
               {'name': 'АК АЛРОСА', 'ticker': 'ALRS', 'parse_name': 'Алроса'},
               {'name': 'Аэрофлот', 'ticker': 'AFLT', 'parse_name': 'Аэрофлот'},
               {'name': 'Банк ВТБ', 'ticker': 'VTBR', 'parse_name': 'ВТБ, Втб'},
               {'name': 'Газпром', 'ticker': 'GAZP', 'parse_name': 'Газпром'},
               {'name': 'Группа Компаний ПИК', 'ticker': 'PIKK', 'parse_name': 'ПИК'},
               {'name': 'Детский мир', 'ticker': 'DSKY', 'parse_name': 'Детский мир'},
               {'name': 'Интер РАО ЕЭС ОАО', 'ticker': 'IRAO', 'parse_name': 'Интер'},
               {'name': 'ЛУКОЙЛ', 'ticker': 'LKOH', 'parse_name': 'Лукойл, ЛУКОЙЛ'},
               {'name': 'М.видео', 'ticker': 'MVID', 'parse_name': 'М.Видео, МВидео, М. Видео'},
               {'name': 'Магнит', 'ticker': 'MGNT', 'parse_name': 'Магнит'},
               {'name': 'МегаФон ОАО', 'ticker': 'MFON', 'parse_name': 'Мегафон, МегаФон'},
               {'name': 'Мечел', 'ticker': 'MTLR', 'parse_name': 'Мечел'},
               {'name': 'МКБ', 'ticker': 'CBOM', 'parse_name': 'МКБ, Московский кредитный банк'},
               {'name': 'ММК ОАО', 'ticker': 'MAGN', 'parse_name': 'ММК'},
               {'name': 'Московская биржа', 'ticker': 'MOEX', 'parse_name': 'Московская биржа'},
               {'name': 'МТС', 'ticker': 'MTSS', 'parse_name': 'МТС'},
               {'name': 'НЛМК ОАО', 'ticker': 'NLMK', 'parse_name': 'НЛМК'},
               {'name': 'НМТП ОАО', 'ticker': 'NMTP', 'parse_name': 'НМТП'},
               {'name': 'НОВАТЭК', 'ticker': 'NVTK', 'parse_name': 'Новатек'},
               {'name': 'Норильский никель', 'ticker': 'GMKN', 'parse_name': 'Норильский никель, Норникель'},
               {'name': 'НПК ОВК', 'ticker': 'UWGN', 'parse_name': 'ОВК'},
               {'name': 'Polymetal', 'ticker': 'POLY', 'parse_name': 'Полиметал, Polymetal'},
               {'name': 'Полюс', 'ticker': 'PLZL', 'parse_name': 'Полюс'},
               {'name': 'РОС АГРО ПЛС', 'ticker': 'AGRO', 'parse_name': 'АГРО ПЛС'},
               {'name': 'Роснефть', 'ticker': 'ROSN', 'parse_name': 'Роснефть'},
               {'name': 'Россети', 'ticker': 'RSTI', 'parse_name': 'Россети'},
               {'name': 'Ростелеком', 'ticker': 'RTKM', 'parse_name': 'Ростелеком'},
               {'name': 'РУСАЛ', 'ticker': 'RUAL', 'parse_name': 'Русал'},
               {'name': 'РусГидро', 'ticker': 'HYDR', 'parse_name': 'РусГидро'},
               {'name': 'РуссНефть', 'ticker': 'RNFT', 'parse_name': 'РуссНефть'},
               {'name': 'Сбербанк', 'ticker': 'SBER', 'parse_name': 'Сбербанк'},
               {'name': 'Северсталь', 'ticker': 'CHMF', 'parse_name': 'Северсталь'},
               {'name': 'Система', 'ticker': 'AFKS', 'parse_name': 'АФК Система'},
               {'name': 'Сургутнефтегаз', 'ticker': 'SNGS', 'parse_name': 'Сургутнефтегаз'},
               {'name': 'Татнефть', 'ticker': 'TATN', 'parse_name': 'Татнефть'},
               {'name': 'ТМК ОАО ', 'ticker': 'TRMK', 'parse_name': 'ТМК'}, {'ticker': 'TRNFP', 'parse_name': 'Транснефть'},
               {'name': 'ФосАгро', 'ticker': 'PHOR', 'parse_name': 'ФосАгро'},
               {'name': 'ФСК ЕЭС ОАО', 'ticker': 'FEES', 'parse_name': 'ФСК ЕЭС'},
               {'name': 'Юнипро', 'ticker': 'UPRO', 'parse_name': 'Юнипро'},
               {'name': 'Яндекс', 'ticker': 'YNDX', 'parse_name': 'Яндекс'}]
    for t in tickers:
        df = pd.read_csv('./../../data/parsed_{0}.csv'.format(t["ticker"]))
        df = df.dropna()
        x = df.iloc[:, 1:-2]
        y = df.iloc[:, -2]
        x_ = sm.add_constant(x)
        smm = sm.OLS(y, x_)
        res = smm.fit()
        p = res.params
        # print(t)
        # print(p)
        t["coef"] = p.to_dict()
        t["pvalues"] = res.pvalues.to_dict()
    with open('./../../data/companies.pickle', 'wb') as companies_file:
        pickle.dump(tickers, companies_file)


if __name__ == '__main__':
    calculate_linreg_coef_and_pvalues()
    calculate_percent_true()
