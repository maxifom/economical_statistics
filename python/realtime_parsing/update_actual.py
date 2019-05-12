"""
    Gets actual price on real-time predictions to calculate accuracy
"""
from datetime import timedelta, datetime

from models import Prediction, Price, fn


def update_predictions():
    predictions = Prediction.select().where(
        (Prediction.actual == 0))
    for p in predictions:
        # Monday = 0, Sunday = 6
        # If Friday or Saturday or Sunday then search for Monday
        if 4 <= p.time.weekday() <= 6:
            for i in [0, 1, 2, 3, 4, 5, 6]:
                price = Price.select(Price.current).where(
                    (Price.time > p.time) & (fn.WEEKDAY(Price.time) == i) & (Price.company == p.company)).order_by(
                    Price.id.desc()).limit(1)
                if len(price) > 0 or (p.time + timedelta(days=i)) > datetime.now():
                    break
        else:
            for i in [1, 2, 3, 4, 5, 6]:
                weekday = (p.time.weekday() + i) % 7
                price = Price.select(Price.current, Price.time).where(
                    (Price.time > p.time) & (
                            fn.WEEKDAY(Price.time) == weekday) & (Price.company == p.company)).order_by(
                    Price.id.desc()).limit(1)
                if len(price) > 0 or p.time + timedelta(days=i) > datetime.now():
                    break
        price = price[0] if len(price) > 0 else None
        if price is not None:
            p.actual = price.current
            p.actual_price_time = price.time
            p.save()


if __name__ == '__main__':
    update_predictions()
    print("predictions updated")
