# -*- coding: utf-8 -*-

from __future__ import with_statement
from flask import Flask, request, redirect, url_for, render_template, flash
from docutils.writers.html4css1 import Writer
import docutils.core
import os


app = Flask(__name__)


@app.route('/')
def index():
    models = {}

    for categ in os.listdir('static/model'):
        models[categ] = []
        for model in os.listdir('static/model/' + categ):
            models[categ].append(model)
    return render_template('index.html', models=models)


@app.route('/edit/<category>/<filename>')
def edit(category, filename):
    return rest_to_html(category, filename)


def rest_to_html(category, filename):
    parts = docutils.core.publish_parts(
        source=open(os.path.join(
            'static', 'model', category, filename + '.rst')).read(),
        writer=Writer())
    text = parts['html_body']
    return text


if __name__ == '__main__':
    app.secret_key = 'MNOPQR'
    app.run(debug=True)
