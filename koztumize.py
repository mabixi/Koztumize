# -*- coding: utf-8 -*-

from __future__ import with_statement
from flask import Flask, request, redirect, url_for, render_template, flash
import os


app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def index():
    models = {}

    for categ in os.listdir('static/model'):
        models[categ] = []
        for model in os.listdir('static/model/' + categ):
            models[categ].append(model)

    return render_template('index.html', models=models)


if __name__ == '__main__':
    app.secret_key = 'MNOPQR'
    app.run(debug=True)
