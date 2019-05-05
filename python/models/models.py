import datetime
import os

from peewee import *

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

dbhandle = MySQLDatabase(database=database, user=user, password=password, host=host)


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Company(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(unique=True)
    full_name = CharField()
    parse_name = CharField()
    ticker = CharField()
    url = CharField()
    finam_id = IntegerField()
    linear_model = TextField(default="{}")
    arima_model = TextField(default="{}")

    class Meta:
        db_table = "companies"


class News(BaseModel):
    id = PrimaryKeyField(null=False)
    company = ForeignKeyField(model=Company)
    link = CharField()
    body = TextField()
    title = TextField()
    time = DateTimeField()
    sent_score = DecimalField(30, 12)
    word_count = IntegerField()
    parsed_sentence = TextField()
    words = TextField()

    class Meta:
        db_table = "news"


class Prediction(BaseModel):
    id = PrimaryKeyField(null=False)
    company = ForeignKeyField(model=Company)
    mean_trading_day_variation = DecimalField(30, 12)
    mean_sent_score = DecimalField(30, 12)
    mean_word_count = DecimalField(30, 12)
    mean_trading_volume = DecimalField(30, 12)
    mean_overnight_variation = DecimalField(30, 12)
    mean_log_return = DecimalField(30, 12)
    mean_closing_price = DecimalField(30, 12)
    prediction = DecimalField(30, 12)
    current = DecimalField(30, 12)
    actual = DecimalField(30, 12, default=0)
    time = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        db_table = "predictions"


class Price(BaseModel):
    id = PrimaryKeyField(null=False)
    company = ForeignKeyField(model=Company)
    current = DecimalField(15, 8)
    high = DecimalField(15, 8)
    low = DecimalField(15, 8)
    volume = DecimalField(15, 8)
    volume_previous = DecimalField(15, 8)
    time = DateTimeField()

    class Meta:
        db_table = "prices"


class Word(BaseModel):
    id = PrimaryKeyField(null=False)
    word = CharField(unique=True)
    is_positive = BooleanField()

    class Meta:
        db_table = "words"
# if __name__ == '__main__':
# price = Price.select(Price, Company).join(Company).get()
# print(price.company.name)
