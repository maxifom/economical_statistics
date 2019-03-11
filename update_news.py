import os

import analysis
import spiders
from database import Database


def update_counter(current_timestamp):
    current_timestamp = int(current_timestamp)
    if not os.path.exists("./news_count"):
        with open("./news_count", 'w') as news_count:
            news_count.write(str(current_timestamp))
            return -1
    else:
        with open("./news_count", 'r+') as news_count:
            last_timestamp = int(news_count.read())
            if last_timestamp != current_timestamp:
                news_count.seek(0)
                news_count.write(str(current_timestamp))
                news_count.truncate()
                return last_timestamp
    return 0


def update_actual_on_news():
    db = Database()
    db.db.execute("""
        SELECT id, company_id, UNIX_TIMESTAMP(time)+300 as t FROM news WHERE actual IS NULL AND (UNIX_TIMESTAMP() - UNIX_TIMESTAMP(time)) >= 300
    """)
    news_without_actual = db.db.fetchall()
    if len(news_without_actual) > 0:
        print("Updating " + str(len(news_without_actual)) + " news")
        for n in news_without_actual:
            db.db.execute("""
                SELECT current,time FROM prices WHERE company_id = %s AND UNIX_TIMESTAMP(time) >= %s ORDER BY id ASC LIMIT 1
            """, (n["company_id"], int(n["t"])))
            row = db.db.fetchone()
            actual = row["current"]
            db.db.execute("""
                UPDATE news SET actual = %s WHERE id = %s
            """, (actual, n["id"]))
        db.connection.commit()


if __name__ == '__main__':
    news = spiders.get_news()
    current_timestamp = 0
    for n in news:
        current_timestamp = max(current_timestamp, n["timestamp"])
    last_timestamp = update_counter(current_timestamp)
    news_to_update = list()
    if last_timestamp == -1:
        news_to_update = news
    elif last_timestamp != 0:
        for n in news:
            if n["timestamp"] > last_timestamp:
                news_to_update.append(n)
    if len(news_to_update) > 0:
        for n in news_to_update:
            n["info"] = analysis.sentence_info(n["text"])
        news_to_update = analysis.get_news_company_id(news_to_update)
        db = Database()
        print(news_to_update)
        for n in news_to_update:
            db.db.execute("""
                INSERT INTO news(id, company_id, link,body, prediction, actual, time, sent_score, word_count, log_return, trading_volume, overnight_variation, trading_day_variation, closing_price)
                VALUES (NULL, %s, %s,%s,NULL,NULL,FROM_UNIXTIME(%s),%s,%s,NULL,NULL,NULL,NULL,NULL)
            """, (n["companies"].copy().pop(), n["url"], n["text"].encode("utf-8"), n["timestamp"], n["info"]["score"],
                  n["info"]["count"]))
            db.connection.commit()
        analysis.calculate_predictions(news_to_update)

    update_actual_on_news()
