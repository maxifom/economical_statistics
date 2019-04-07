from database import Database

def update_actual():
    db = Database()
    db.db.execute("""
        SELECT * FROM predictions WHERE actual = 0
    """)
    without_actual_predictions = db.db.fetchall()
    for p in without_actual_predictions:
        db.db.execute("""
            SELECT current FROM prices WHERE company_id = %s ORDER BY id DESC LIMIT 1
        """, (p["company_id"],))
        current_price = db.db.fetchone()["current"]
        db.db.execute("""
            UPDATE predictions SET actual = %s WHERE id = %s
        """, (current_price, p["id"]))
        db.connection.commit()


if __name__ == '__main__':
    update_actual()
