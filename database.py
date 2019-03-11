import os
from datetime import datetime

import MySQLdb
import MySQLdb.cursors


class Database:
    def __init__(self):
        host = os.getenv("MYSQL_HOST", "localhost")
        connection = MySQLdb.connect(host, 'user', 'user', 'economics', cursorclass=MySQLdb.cursors.DictCursor)
        self.connection = connection
        self.db = self.connection.cursor()
        self.connection.encoding = 'utf-8'
        self.db.execute('''
            SET NAMES utf8;
            SET CHARACTER SET utf8;
            SET character_set_connection=utf8;
        ''')
        # if os.path.exists('./schema.sql'):
        #     with open('./schema.sql', 'r', encoding='utf-8') as schema:
        #         self.db.execute(schema.read().replace('\n', ''))

    def insert_companies(self, given_companies):
        self.db.execute("""
            SELECT COUNT(1) as count FROM companies
        """)
        count = self.db.fetchone()["count"]
        if count == 0:
            for name, company in given_companies.items():
                self.db.execute("""
                    INSERT INTO companies (name,full_name)
                    VALUES (%s,%s)
                """, (name.encode('utf-8'), company["full_name"].encode('utf-8')))

            self.connection.commit()
        self.db.execute("""
            SELECT * from companies
        """)
        companies = self.db.fetchall()
        for company in companies:
            given_companies[company["name"]]["id"] = company["id"]
        for name, company in given_companies.items():
            self.db.execute("""
                SELECT company_id, volume,time FROM prices 
                WHERE company_id = %s ORDER BY id DESC LIMIT 1
            """, (company["id"],))
            last = self.db.fetchone()
            company_time = datetime.utcfromtimestamp(company["time"])
            if not last or company_time != last["time"]:
                if not last:
                    last_volume = company["volume"]
                else:
                    last_volume = last["volume"]
                self.db.execute("""
                    INSERT INTO prices(company_id, current,high,low,volume,volume_previous,time)
                    VALUES (%s,%s,%s,%s,%s,%s, FROM_UNIXTIME(%s))
                """, (company["id"],
                      company["current_price"],
                      company["high_price"],
                      company["low_price"],
                      company["volume"],
                      company["volume"] - last_volume,
                      company["time"],
                      ))
        self.connection.commit()
        return

    def get_all_companies(self):
        self.db.execute("""
            SELECT * FROM companies
        """)
        return self.db.fetchall()

    def __del__(self):
        self.connection.close()
