import os
import pickle

import pandas as pd
from flask import Flask, render_template, request, redirect
from database import Database
from add_to_dictionary import *
from analysis import sentence_info

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/companies")
@app.route("/companies/<company>")
def companies(company=None):
    db = Database()
    coefs = None
    pvalues = None
    if company is None:
        cs = db.get_all_companies()
    else:
        cs = db.get_company_by_id_with_price(company)
        with open('./../data/companies.pickle', 'rb') as f:
            companies = pickle.load(f)
        l = list(filter(lambda c: c["ticker"] == cs[0]["ticker"], companies))
        if len(l) > 0:
            c = l[0]
            coefs = c["coef"]
            pvalues = c['pvalues']
        else:
            coefs = None
            pvalues = None
    return render_template('companies.html', companies=cs, coefs=coefs, pvalues=pvalues)


@app.route("/news")
@app.route("/news/<n>")
def news(n=None):
    db = Database()
    info = None
    if n is None:
        ns = db.get_all_news()
    else:
        ns = db.get_news_by_id(n)
        with open('./../data/news_' + str(n) + '_words', 'rb') as f:
            info = pickle.load(f)
    return render_template('news.html', news=ns, info=info)


@app.route("/dict", methods=["GET", "POST"])
def dict():
    if request.method == 'POST':
        f = request.files['file']
        type = request.form['type']
        if type == 'positive':
            f.save('./positive.txt')
            positive_from_txt('./positive.txt')
        elif type == 'negative':
            f.save('./negative.txt')
            negative_from_txt('./negative.txt')
        return redirect('/dict')
    else:
        percents = None
        if os.path.exists('./../data/result.pickle'):
            with open('./../data/result.pickle', 'rb') as f:
                percents = pickle.load(f)
        percents['values'] = sorted(percents['values'], key=lambda p: p["percent"])
        db = Database()
        db.db.execute("""
            SELECT * FROM words ORDER BY id DESC
        """)
        dict = db.db.fetchall()
        if os.path.exists('./is_parsing'):
            with open('./is_parsing', 'r') as f:
                if f.read() == '1':
                    status = 'parsing'
                else:
                    status = 'not parsing'
        else:
            status = 'not parsing'
        return render_template('dict.html', dict=dict, status=status, percents=percents)


@app.route("/delete", methods=["POST"])
def delete():
    if request.method == "POST":
        db = Database()
        id = request.form["id"]
        db.db.execute("""DELETE FROM words WHERE id = %s""", (id,))
        db.connection.commit()
        return redirect('/dict')
    else:
        return ''


@app.route("/reparse", methods=["POST"])
def reparse():
    if request.method == "POST":
        if os.path.exists('./is_parsing'):
            with open('./is_parsing', 'r') as file:
                if int(file.read()) != 1:
                    with open('./is_parsing', 'w') as file:
                        file.write(str(1))
                    with open('./need_parsing', 'w') as file:
                        file.write(str(1))
                    return 'Parsing started'
                else:
                    return 'Already parsing'
        else:
            with open('./is_parsing', 'w') as file:
                file.write(str(1))
            with open('./need_parsing', 'w') as file:
                file.write(str(1))
            return 'Parsing started'
    else:
        return ''


@app.route('/history')
@app.route('/history/<page>')
def history(page=0):
    df = pd.read_csv('./../data/news_with_one_company_sent_scores.csv')
    df_dict = df.to_dict(orient='rows')
    page = int(page)
    ns = df_dict[page * 10:page * 10 + 10]
    for i in range(0, len(ns)):
        ns[i]["info"] = sentence_info(ns[i]["text"])
        ns[i]["id"] = page * 10 + i
    return render_template("news_history.html", news=ns, page=page)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
