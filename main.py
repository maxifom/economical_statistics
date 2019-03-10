import analysis
import spiders

if __name__ == '__main__':
    news = spiders.parse_companies_and_get_news()
    print(news)
    print(analysis.linear_regression(news))
