from flask import (
    render_template,
    Response,
)
from flask import Flask
from flask import request, redirect, url_for
import requests
import csv
import pickle
import time
import logging
from io import StringIO

logging.basicConfig(level = logging.DEBUG, format="%(levelname)s %(asctime)s - %(message)s", filemode = "w", filename = 'kalkulator_walut_9.2.log',)
logger = logging.getLogger()


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('marta_config.cfg', silent=True)


def get_data():
    try:
        with open('datadump.pickle', 'rb') as cache:
            timestamp, data = pickle.load(cache)
            if timestamp < time.time() - 24*60*60:
                raise ValueError("Stale cache")
            logging.info("File got found")
            return data
    except (FileNotFoundError, ValueError) as error:
        logging.error("File not found")
        print(error)
        response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
        data = response.json()[0]['rates']
        with open('datadump.pickle', 'wb') as cache:
            pickle.dump((time.time(), data), cache)
        return data


@app.route("/", methods=["GET", "POST"])
def currency_calculator():
    data = get_data()

    codes = []
    for item in data:
        codes.append(item['currency'])

    message = ""

    if request.method == "POST":
        bid_rate =""
        data_form = request.form
        try:
            amount = float(data_form.get('amount'))
        except ValueError as error:
            return render_template("kalkulator_walut2.html", codes=codes, message=str(error))

        currency = data_form.get('currency_value')

        for item in data:
            if item['currency'] == currency:
                bid_rate = float(item['bid'])
                break

        message = f" {round(amount * (bid_rate),2)} PLN"

    return render_template("kalkulator_walut2.html", codes=codes, message=message)

@app.route("/notowania.csv", methods=["GET"])
def download():
    data = get_data()

    csvfile = StringIO()
    fieldnames = ['currency', 'code', 'bid', 'ask']
    csv_writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
    csv_writer.writeheader()
    for item in data:
        csv_writer.writerow(item)
    return Response(csvfile.getvalue(), mimetype='text/csv')

@app.errorhandler(404)
def not_found(error):
    logging.error("Wrong page")
    return render_template('404.html')

@app.errorhandler(500)
def internal_error(error):
    logging.error("Send empty form")
    return render_template('500.html')

if __name__ == "__main__":
    app.run(debug=True)