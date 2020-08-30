from flask import render_template
from flask import flash, Flask
from flask import request, redirect, url_for
import requests
import csv
import pickle


app = Flask(__name__)

def get_data():
    response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    return response.json()[0]['rates']

def kalkutator_wal():
    data = get_data()

    with open('datadump.pickle', 'wb') as csvfile:
        pickle.dump(data, csvfile)
    with open('datadump.pickle', 'rb') as csvfile:
        data= pickle.load(csvfile)
        

kalkutator_wal()