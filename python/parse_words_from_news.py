import pickle

from database import Database
from analysis import sentence_info


def parse_news():
    db = Database()
    db.db.execute("""
        SELECT id, body FROM news WHERE parsed=0
    """)
    news = db.db.fetchall()
    if news is None:
        return
    for n in news:
        info = sentence_info(n["body"])
        words_with_polarity = info["words"]
        with open('./../data/news_' + str(n["id"]) + '_words', 'wb') as f:
            pickle.dump(info, f)
    db.db.execute("UPDATE news SET parsed = 1")
    db.connection.commit()


if __name__ == '__main__':
    parse_news()
