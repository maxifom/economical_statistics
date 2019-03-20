import pandas as pd

if __name__ == '__main__':
    parse_names = [{'ticker': 'SFIN', 'parse_name': 'Сафмар, Safmar'}, {'ticker': 'FIVE', 'parse_name': 'X5'},
                   {'ticker': 'ALRS', 'parse_name': 'Алроса'}, {'ticker': 'AFLT', 'parse_name': 'Аэрофлот'},
                   {'ticker': 'VTBR', 'parse_name': 'ВТБ, Втб'}, {'ticker': 'GAZP', 'parse_name': 'Газпром'},
                   {'ticker': 'PIKK', 'parse_name': 'ПИК'}, {'ticker': 'DSKY', 'parse_name': 'Детский мир'},
                   {'ticker': 'IRAO', 'parse_name': 'Интер'}, {'ticker': 'LKOH', 'parse_name': 'Лукойл, ЛУКОЙЛ'},
                   {'ticker': 'MVID', 'parse_name': 'М.Видео, МВидео, М. Видео'},
                   {'ticker': 'MGNT', 'parse_name': 'Магнит'}, {'ticker': 'MFON', 'parse_name': 'Мегафон, МегаФон'},
                   {'ticker': 'MTLR', 'parse_name': 'Мечел'},
                   {'ticker': 'CBOM', 'parse_name': 'МКБ, Московский кредитный банк'},
                   {'ticker': 'MAGN', 'parse_name': 'ММК'}, {'ticker': 'MOEX', 'parse_name': 'Московская биржа'},
                   {'ticker': 'MTSS', 'parse_name': 'МТС'}, {'ticker': 'NLMK', 'parse_name': 'НЛМК'},
                   {'ticker': 'NMTP', 'parse_name': 'НМТП'}, {'ticker': 'NVTK', 'parse_name': 'Новатек'},
                   {'ticker': 'GMKN', 'parse_name': 'Норильский никель, Норникель'},
                   {'ticker': 'UWGN', 'parse_name': 'ОВК'}, {'ticker': 'POLY', 'parse_name': 'Полиметал, Polymetal'},
                   {'ticker': 'PLZL', 'parse_name': 'Полюс'}, {'ticker': 'AGRO', 'parse_name': 'АГРО ПЛС'},
                   {'ticker': 'ROSN', 'parse_name': 'Роснефть'}, {'ticker': 'RSTI', 'parse_name': 'Россети'},
                   {'ticker': 'RTKM', 'parse_name': 'Ростелеком'}, {'ticker': 'RUAL', 'parse_name': 'Русал'},
                   {'ticker': 'HYDR', 'parse_name': 'РусГидро'}, {'ticker': 'RNFT', 'parse_name': 'РуссНефть'},
                   {'ticker': 'SBER', 'parse_name': 'Сбербанк'}, {'ticker': 'CHMF', 'parse_name': 'Северсталь'}, {'ticker': 'AFKS', 'parse_name': 'АФК Система'},
                   {'ticker': 'SNGS', 'parse_name': 'Сургутнефтегаз'}, {'ticker': 'TATN', 'parse_name': 'Татнефть'},
                   {'ticker': 'TRMK', 'parse_name': 'ТМК'},
                   {'ticker': 'TRNFP', 'parse_name': 'Транснефть'}, {'ticker': 'PHOR', 'parse_name': 'ФосАгро'},
                   {'ticker': 'FEES', 'parse_name': 'ФСК ЕЭС'}, {'ticker': 'UPRO', 'parse_name': 'Юнипро'},
                   {'ticker': 'YNDX', 'parse_name': 'Яндекс'}]
    for p in parse_names:
        p['parse_name'] = p['parse_name'].split(', ')
    df = pd.read_csv('./csv/all_parsed_news_with_sentiment_scores.csv')
    df_dict = df.to_dict(orient='rows')
    news_with_one_company = list()
    news_with_one_plus_company = list()
    for d in df_dict:
        d["companies"] = list()
        for company in parse_names:
            for p in company["parse_name"]:
                if p in str(d["text"]):
                    d["companies"].append(company['ticker'])
                    break
        if len(d["companies"]) == 1:
            d["companies"] = d["companies"][0]
            news_with_one_company.append(d)
        if len(d["companies"]) > 0:
            news_with_one_plus_company.append(d)
    one_company_df = pd.DataFrame(news_with_one_company,
                                  columns=['companies', 'sent_score', 'text', 'timestamp', 'url', 'word_count']).sort_values(by="timestamp").reset_index(drop=True)
    one_company_plus_df = pd.DataFrame(news_with_one_plus_company,
                                       columns=['companies', 'sent_score', 'text', 'timestamp', 'url', 'word_count']).sort_values(by="timestamp").reset_index(drop=True)
    one_company_df.to_csv('./csv/news_with_one_company.csv')
    one_company_plus_df.to_csv('./csv/news_with_one_or_more_company.csv')