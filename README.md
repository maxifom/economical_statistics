# Economical Statistics project

Current Trend Accuracy: 52.2% with linear regression

History values are located in linreg.csv

News from Jan 1 2017 to Mar 9 2019 from site finam.ru used
## News Criteria
* Publication time is from 9:59MSK to 19:00MSK
* Publication date is from Mon to Fri
* The MOEX was open (there is valid history that day)
* Contains only one company

## Libraries used
* For semantic analysis - [polyglot](https://github.com/aboSamoor/polyglot)
* For lemmatisation - [pymorphy](https://github.com/kmike/pymorphy2)
* For calculating linear regression - [statsmodels](https://github.com/statsmodels/statsmodels)

## Software used
* Mysql for storing companies, stock prices and news (for future real-time processing of news)
