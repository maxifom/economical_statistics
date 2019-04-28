import pickle

from misc.database import Database
from polyglot.text import Text

from misc.analysis import sentence_info


def parse_news():
    db = Database()
    db.db.execute("""
        SELECT id, body FROM news
    """)
    news = db.db.fetchall()
    if news is None:
        return
    for n in news:
        info = sentence_info(n["body"])
        words_with_polarity = info["words"]
        # words_with_polarity = list()
        # t = Text(text=n["body"].encode('utf-8'), hint_language_code='ru')
        # for w in t.words:
        #     _w = dict()
        #     _w["word"] = w
        #     _w["polarity"] = w.polarity
        #     words_with_polarity.append(w)
        with open('./../../data/news_' + str(n["id"]) + '_words', 'wb') as f:
            pickle.dump(info, f)
        db.db.execute("""UPDATE news SET sent_score = %s, word_count = %s WHERE id = %s""",
                      (info["sent_score"], info["word_count"], n["id"]))
    db.db.execute("UPDATE news SET parsed = 1")
    db.connection.commit()


if __name__ == '__main__':
    parse_news()
