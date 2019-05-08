"""
    Gets actual price on real-time predictions to calculate accuracy
"""

from models import Prediction, Price, fn


def update_predictions():
    predictions = Prediction.select().where(
        (Prediction.actual == 0))
    for p in predictions:
        # Monday = 0, Sunday = 6
        # If Friday or Saturday or Sunday then search for Monday
        if 4 <= p.time.weekday() <= 6:
            price = Price.select(Price.current).where(
                (Price.time > p.time) & (fn.WEEKDAY(Price.time) == 0) & (Price.company == p.company)).order_by(
                Price.id.desc()).limit(1)
        else:
            weekday = (p.time.weekday() + 1) % 7
            price = Price.select(Price.current).where(
                (Price.time > p.time) & (
                        fn.WEEKDAY(Price.time) == weekday) & Price.company == p.company).order_by(
                Price.id.desc()).limit(1)
        price = price[0].current if len(price) > 0 else None
        if price is not None:
            p.actual = price
            p.save()


if __name__ == '__main__':
    update_predictions()
    print("predictions updated")
