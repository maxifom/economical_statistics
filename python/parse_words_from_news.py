import pickle

from database import Database
from polyglot.text import Text


def parse_news():
    db = Database()
    db.db.execute("""
        SELECT id, body FROM news WHERE parsed=0
    """)
    news = db.db.fetchall()
    if news is None:
        return
    for n in news:
        words_with_polarity = list()
        t = Text(text=n["body"].encode('utf-8'), hint_language_code='ru')
        for w in t.words:
            _w = dict()
            _w["word"] = w
            _w["polarity"] = w.polarity
            words_with_polarity.append(w)
        with open('./../data/news_' + str(n["id"]) + '_words', 'wb') as f:
            pickle.dump(words_with_polarity, f)
    db.db.execute("UPDATE news SET parsed = 1")
    db.connection.commit()


if __name__ == '__main__':
    parse_news()
