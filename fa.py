# -*- coding: utf-8 -*-

from __future__ import with_statement
from flask import Flask, request, redirect, url_for, render_template, flash
import os


app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def index():
    list_courrier = os.listdir('static/courrier')
    list_facture = os.listdir('static/facture')
    return render_template('index.html',
        list_courrier=list_courrier, list_facture=list_facture)


if __name__ == '__main__':
    app.secret_key = 'MNOPQR'
    app.run(debug=True)
