from flask import render_template
from flask import flash, Flask
from flask import request, redirect, url_for
import requests
import csv
import pickle
import time


app = Flask(__name__)

def get_data():
    try:
        with open('datadump.pickle', 'rb') as cache:
            timestamp, data = pickle.load(cache)
            if timestamp < time.time() - 5:
                raise ValueError("Stale cache")
            return data
    except (FileNotFoundError, ValueError) as error:
        print(error)
        response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
        data = response.json()[0]['rates']
        with open('datadump.pickle', 'wb') as cache:
            pickle.dump((time.time(), data), cache)
        return data


@app.route("/", methods=["GET", "POST"])
def currency_calculator():
    data = get_data()

    with open('datadump.csv', 'w', newline='', encoding='utf8') as csvfile:
        fieldnames = ['currency', 'code', 'bid', 'ask']
        csv_writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in data:
            csv_writer.writerow(item)

    
    codes = []
    for item in data:
        codes.append(item['currency'])

    message = ""

    if request.method == "POST":
        bid_rate =""
        data_form = request.form
        amount = float(data_form.get('amount'))
        currency = data_form.get('currency_value')

        for item in data:
            if item['currency'] == currency:
                bid_rate = round(float(item['bid']),2)
                break

        message = f" {amount * bid_rate} PLN"

    return render_template("kalkulator_walut2.html", codes=codes, message=message)


if __name__ == "__main__":
    app.run(debug=True)