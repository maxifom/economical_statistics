from database import Database

if __name__ == '__main__':
    db = Database()
    db.db.execute("""
                SELECT prediction, actual, current FROM predictions WHERE company_id = %s AND actual != 0
            """, (1,))
    d = db.db.fetchall()
    prediction = dict()
    prediction["count"] = len(d)
    prediction["true"] = 0
    for _d in d:
        first = _d["prediction"] > _d["current"]
        second = _d["actual"] > _d["current"]
        if first == second:
            prediction["true"] += 1
