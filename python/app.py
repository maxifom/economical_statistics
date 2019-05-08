import json

import pandas as pd
from flask import Flask, render_template, request, redirect, make_response, send_from_directory
from misc.add_to_dictionary import add_words_from_txt, process_lines, process_line
from models.models import *
from realtime_parsing.predict import predict
from realtime_parsing.update_actual import update_predictions

app = Flask(__name__)


@app.route("/<path:path>")
def asset(path):
    return send_from_directory("assets", path)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/icons/<icon>")
def icons(icon):
    return send_from_directory('./icons/', icon)


@app.route("/companies")
def companies():
    companies = Company.select()
    return render_template('companies.html', companies=companies)


@app.route("/company/<id>")
def company(id=1):
    company = Company.get(Company.id == id)
    price = Price.select().order_by(Price.id.desc()).where(Price.company == company.id).get()
    company.price = price
    news = News.select().where(News.company == company.id).order_by(News.id.desc())
    company.news = news
    company.linear_model = json.loads(company.linear_model)
    return render_template('company.html', company=company)


@app.route("/news")
@app.route("/news/<page>")
def news(page=0):
    page = int(page)
    ns = News.select(News, Company).join(Company).order_by(News.id.desc()).limit(10).offset(page * 10)
    return render_template('news.html', news=ns, page=page)


@app.route("/news_single/<id>")
def news_single(id=1):
    news = News.get(News.id == id)
    news.words = json.loads(news.words)
    return render_template('news_single.html', news=news)


@app.route("/add_words", methods=["POST"])
def add_words():
    resp = make_response(redirect('/dict'))
    # Check code and type
    if "code" in request.form and request.form["code"] == os.environ.get("DELETE_CODE"):
        if "type" in request.form:
            type = request.form["type"]
            is_positive = 1 if type == "positive" else 0
            resp.set_cookie('code', request.form["code"])
        else:
            return resp
    else:
        return resp
    # From textarea
    if "text" in request.form and request.form["text"].replace(" ", "") != "":
        text = request.form["text"]
        lines = text.split("\n")
        process_lines(lines, is_positive)
        return resp
    # From file
    elif "file" in request.files and request.files['file'].filename != '':
        f = request.files['file']
        f.save('./words.txt')
        add_words_from_txt('./words.txt', is_positive)
        os.remove('./words.txt')
        return resp
    # Single word
    elif "single_word" in request.form and request.form["single_word"] != "":
        process_line(request.form["single_word"], is_positive)
        return resp
    return resp


@app.route("/visualization")
def visualization():
    companies = Company.select()
    for c in companies:
        c.linear_model = json.loads(c.linear_model)
        c.arima_model = json.loads(c.arima_model)
    with open("./../data/word_cloud/word_cloud.json", "r") as file:
        word_cloud = json.load(file)
    return render_template('visualization.html',
                           companies=companies,
                           all_words=word_cloud["all_words"],
                           pos_words=word_cloud["positive_words"], neg_words=word_cloud["negative_words"])


@app.route("/dict", methods=["GET"])
def dict():
    words = Word.select().order_by(Word.id.desc())
    with open("./../data/word_cloud/word_cloud.json", "r") as file:
        word_cloud = json.load(file)
    return render_template('dict.html', words=words,
                           all_words=word_cloud["all_words"],
                           pos_words=word_cloud["positive_words"], neg_words=word_cloud["negative_words"])


@app.route("/delete", methods=["POST"])
def delete():
    resp = make_response(redirect('/dict'))
    if "code" in request.form and request.form["code"] == os.environ.get("DELETE_CODE") and "id" in \
            request.form:
        id = request.form["id"]
        Word.get_by_id(id).delete_instance()
        resp.set_cookie('code', request.form["code"])
    return resp


@app.route('/history')
@app.route('/history/<page>')
def history(page=0):
    page = int(page)
    df = pd.read_csv('./../data/news/news_with_one_company_and_sentiment_analysis.csv',
                     skiprows=range(1, page * 10),
                     nrows=10)
    df.title.fillna("0", inplace=True)
    news = df.to_dict(orient='rows')
    id = page * 10 + 1
    for n in news:
        n["words"] = json.loads(n["words"].replace("'", '"'))
        n["id"] = id
        n["date"] = datetime.datetime.utcfromtimestamp(n["timestamp"])
        id += 1
    return render_template("news_history.html", news=news, page=page)


@app.route('/predictions')
def predictions():
    companies = Company.select()
    predictions = list()
    tr = 0
    l = 0
    perc = 0
    for c in companies:
        prediction = Prediction.select(Prediction, Company).join(Company).where(
            Prediction.company == c.id).order_by(
            Prediction.id.desc).limit(1)
        prediction = prediction[0] if len(prediction) > 0 else None
        if prediction is None:
            continue
        prediction.trend = float(prediction.prediction) > float(prediction.current)
        predictions.append(prediction)
        company_predictions = Prediction.select(Prediction).where(
            (Prediction.company == c.id) & (Prediction.actual != 0))
        prediction.count = len(company_predictions)
        prediction.true = 0
        for p in company_predictions:
            first = p.prediction > p.current
            second = p.actual > p.current
            if first == second:
                prediction.true += 1
        if prediction.count == 0:
            prediction.percent = "0"
        else:
            prediction.percent = "{0:.2f}".format(prediction.true / prediction.count * 100)
        tr += prediction.true
        l += prediction.count
        if l != 0:
            perc = "{0:.2f}".format(tr / l * 100)
    predictions = sorted(predictions, key=lambda p: (float(p.percent), float(p.true)), reverse=True)
    return render_template("predictions.html", predictions=predictions, tr=tr, l=l, perc=perc)


@app.route('/all_predictions')
@app.route('/all_predictions/<page>')
def all_predictions(page=0):
    page = int(page)
    predictions = Prediction.select(Prediction, Company).join(Company).order_by(Prediction.id.desc()).limit(
        50).offset(
        50 * page)
    for p in predictions:
        p.trend = float(p.prediction) > float(p.current)
    return render_template("all_predictions.html", predictions=predictions, page=page)


@app.route('/predict')
def predict_now():
    predict()
    return redirect('/predictions')


@app.route('/prediction/<id>')
def prediction(id=1):
    p = Prediction.select(Prediction, Company).join(Company).where(Prediction.id == id).limit(1)
    p = p[0] if len(p) > 0 else None
    if p is None:
        return render_template("prediction.html", prediction=p)
    p.trend = float(p.prediction) > float(p.current)
    p.company.linear_model = json.loads(p.company.linear_model)
    return render_template("prediction.html", p=p)


@app.route("/graphs/<path:path>")
def send_graph(path):
    return send_from_directory('./../data/plots/', path)


@app.route('/update_actual')
def update_actual():
    update_predictions()
    return redirect('/predictions')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
