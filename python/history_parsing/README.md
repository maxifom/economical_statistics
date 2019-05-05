# History parsing and linear regression model training

How to build:
1. Parse news from finam site (parse_finam_news.py)
2. Get history prices from moex (get_history_prices.py)
3. Calculate price parameters (variations, log return) (calculate_price_parameters.py)
4. Extract companies from news (extract_companies_from_news.py)
5. Calculate sentiment scores (calculate_sentiment_scores_on_news.py)
6. Group prices with sentiment scores (group_prices_and_sentiment_scores.py)
7. Calculate linreg model (calculate_linreg_params.py)