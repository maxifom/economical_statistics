import pickle

from flask import Flask, render_template
from database import Database

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
        coefs = companies[cs[0]["id"] - 1]["coef"]
        pvalues = companies[cs[0]["id"] - 1]['pvalues']
    return render_template('companies.html', companies=cs, coefs=coefs, pvalues=pvalues)


@app.route("/news")
@app.route("/news/<n>")
def news(n=None):
    db = Database()
    if n is None:
        ns = db.get_all_news()
    else:
        ns = db.get_news_by_id(n)
    return render_template('news.html', news=ns)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
