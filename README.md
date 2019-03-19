# economical_statistics
Economical statistics project

# Done
* Parsed all news from 2017-01-01, got all companies from the news, calculated sentiment score of news and word count
* Parsed 1 minute and 1 hour canles history from MOEX for all companies since 2017-01-01
* Calculated Linear Regression Coefficients (Prediction True % from 48.2% to 59.2%) and P-values 
* All parsed data and sentiment scores in CSV format: [CSV](https://drive.google.com/open?id=1VvdJM-5Q_2O65xtStWPhj34awS-vKAsc)
* Simple Flash Backend for data visualization (pvalues + linreg coefficient done)
* News update every 2 minutes and price update every 5 minutes
# TODO
1. Real-Time analysis

### History build steps:
* Folder "python/history_parsing"
1. finam_news_parser.py + moex_history_parser.py (News + MOEX candle history)
2. sentiment_analysis.py (Add sentiment scores to news)
3. companies_extractor.py (Add extracted companies to news)
4. linreg_params_final.py (Calculate all historical params for linreg calculation)
5. linreg_coef_final.py (Calculate linreg coefficients + pvalues) -> companies.pickle

### File index
* history_{company_ticker}_1 - 1 minutes candle history
* history_{company_ticker}_24 - 1 day candle history
* all_parsed_news.csv - all parsed news w/o sent scores and companies
* all_parsed_news_with_sentiment_scores.csv - all parsed news with sentiment scores and w/o companies
* news_with_one_company.csv - all parsed news where EXACTLY ONE company exists
* news_with_one_or_more_company.csv - all parsed news where ONE OR MORE companies exist
* parsed_{company_ticker} - Calculated historical parameters for linreg
* companies.pickle - dump of companies list, containing ticker, name, linreg coefs and pvalues

To run full stack app with mysql database, visualization
and real-time news and prices parsing (Take about 2.5GB space):
```sh
docker-compose up -d
```


