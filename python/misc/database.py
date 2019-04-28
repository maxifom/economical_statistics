import os
from datetime import datetime

import MySQLdb
import MySQLdb.cursors


class Database:
    def __init__(self):
        host = os.getenv("MYSQL_HOST")
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")
        connection = MySQLdb.connect(host, user, password, database, cursorclass=MySQLdb.cursors.DictCursor,
                                     charset='utf8', use_unicode=True)
        self.connection = connection
        self.db = self.connection.cursor()

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

    def get_company_by_id(self, id):
        self.db.execute("""
            SELECT * FROM companies WHERE id = %s LIMIT 1
        """, (id,))
        return self.db.fetchall()

    def get_company_by_id_with_price(self, id):
        self.db.execute("""
            SELECT companies.*, prices.current,high,low,volume,volume_previous,time FROM companies INNER JOIN prices ON prices.company_id=companies.id WHERE companies.id = %s ORDER BY prices.id DESC LIMIT 1
        """, (id,))
        company = self.db.fetchall()
        c = company[0]
        self.db.execute("""
                   SELECT * FROM news WHERE company_id = %s ORDER BY time DESC LIMIT 25 
               """, (c["id"],))
        c["news"] = self.db.fetchall()
        return company

    def get_all_news(self):
        self.db.execute("""
               SELECT *, companies.name as company, companies.id as c_id FROM news INNER JOIN companies ON companies.id=news.company_id ORDER BY news.time DESC LIMIT 50
           """)
        return self.db.fetchall()

    def get_news_by_id(self, id):
        self.db.execute("""
               SELECT *,companies.name as company,companies.id as c_id FROM news INNER JOIN companies ON companies.id=news.company_id WHERE news.id = %s LIMIT 1
           """, (id,))
        return self.db.fetchall()

    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()
