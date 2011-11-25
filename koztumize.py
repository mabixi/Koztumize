#!/usr/bin/env python2
"""koztumize.py is used to launch the application Koztumize."""

from flask import (
    Flask, request, render_template, send_file, url_for)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive
import docutils.core
import os
import weasy
import cssutils


app = Flask(__name__)  # pylint: disable=C0103


@app.route('/')
def index():
    """Index is the main route of the application."""
    models = {
        category: os.listdir('static/model/' + category)
        for category in os.listdir('static/model')}
    return render_template('index.html', models=models)


@app.route('/generate', methods=('POST',))
def generate():
    """The route where document .PDF is made with the given HTML and
    the document is return to the client."""
    document = weasy.PDFDocument.from_string(request.form['html_content'])
    document.write_to('tmp/result.pdf')
    return send_file('tmp/result.pdf')


@app.route('/download')
def download():
    """This is the route where you can download the last generated document."""
    return send_file('tmp/result.pdf')


@app.route('/edit/<category>/<filename>')
def edit(category, filename):
    """This is the route where you can edit the models."""
    return render_template('base.html', category=category, filename=filename)


@app.route('/model/<category>/<filename>')
def model(category, filename):
    """This is the route that returns the model."""
    return rest_to_html(category, filename)


def rest_to_html(category, filename):
    """Transform the content of a .rst file in HTML"""
    args = {
        'stylesheet': url_for('static',
                               filename='model_styles/' + filename + '.css',
                               _external=True),
        'stylesheet_path': None,
        'embed_stylesheet': False}
    parts = docutils.core.publish_parts(
        source=open(os.path.join(
            'static', 'model', category, filename + '.rst')).read(),
        writer=Writer(), settings_overrides=args)
    text = parts['whole']
    return text


class Editable(Directive):
    """A rest directive who create an editable div in HTML"""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = (
        '<div contenteditable="true" title="%s"></div>' % (
            self.arguments[0] if self.arguments else ''))
        return [docutils.nodes.raw('', content, format='html')]


class Editable(Directive):
    """A rest directive who create a checkbox in HTML"""
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = '<input type="checkbox"/>'
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('checkbox', Checkbox)
directives.register_directive('editable', Editable)

app.secret_key = 'MNOPQR'

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
