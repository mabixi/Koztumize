#!/usr/bin/env python2
"""koztumize.py is used to launch the application Koztumize."""

from flask import (
    Flask, request, render_template, send_file, url_for, g)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive
import docutils.core
import os
import weasy
from tempfile import NamedTemporaryFile
import argparse


DOMAIN = None
app = Flask(__name__)  # pylint: disable=C0103


@app.before_request
def before_request():
    """Set variables before each request."""
    g.domain = DOMAIN or request.host.split('.')[0]


@app.route('/')
def index():
    """Index is the main route of the application."""
    models = {
        category: os.listdir(os.path.join('static', 'domain',
                                          g.domain, 'model', category))
        for category in os.listdir(os.path.join('static', 'domain',
                                                g.domain, 'model'))}
    return render_template('index.html', models=models)


@app.route('/generate', methods=('POST',))
def generate():
    """The route where document .PDF is made with the given HTML and
the document is return to the client."""
    document = weasy.PDFDocument.from_string(request.form['html_content'])
    temp_file = NamedTemporaryFile(suffix='.pdf', delete=True)
    document.write_to(temp_file)
    return send_file(temp_file.name, as_attachment=True,
                     attachment_filename=request.form['filename'] + '.pdf')


@app.route('/edit/<category>/<filename>')
def edit(category, filename):
    """This is the route where you can edit the models."""
    return render_template('base.html', category=category, filename=filename)


@app.route('/model/<category>/<filename>')
def model(category, filename):
    """This is the route that returns the model."""
    stylesheet = ''
    dom_tree = docutils.core.publish_doctree(source=open(os.path.join(
        'static', 'domain', g.domain, 'model',
         category, filename + '.rst')).read()).asdom()
    list_field = dom_tree.getElementsByTagName('field')
    for field in list_field:
        if (field.childNodes.item(0).childNodes.item(0).nodeValue ==
            'stylesheet'):
            stylesheet = (
                field.childNodes.item(1).childNodes.item(0)
                .childNodes.item(0).nodeValue)

    arguments = {
        'stylesheet': url_for('static',
                              filename=os.path.join('domain', g.domain,
                              'model_styles', stylesheet + '.css'),
                               _external=True),
        'stylesheet_path': None,
        'embed_stylesheet': False}
    parts = docutils.core.publish_parts(
        source=open(os.path.join('static', 'domain', g.domain,
                                 'model', category, filename + '.rst'))
        .read(), writer=Writer(), settings_overrides=arguments)
    text = parts['whole']
    return text


class Editable(Directive):
    """A rest directive who create an editable div in HTML."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = (
        '<div contenteditable="true" title="%s"></div>' % (
            self.arguments[0] if self.arguments else ''))
        return [docutils.nodes.raw('', content, format='html')]


class Checkbox(Directive):
    """A rest directive who create a checkbox in HTML."""
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = (
            '<input type="checkbox" '
            'onChange="this.setAttribute('
            '\'checked\', this.checked?\'checked\':\'\');"/>')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('checkbox', Checkbox)
directives.register_directive('editable', Editable)

app.secret_key = 'MNOPQR'

if __name__ == '__main__':  # pragma: no cover
    arg_parser = argparse.ArgumentParser()  # pylint: disable=C0103
    arg_parser.add_argument('project', nargs='?', help='project name')
    args = arg_parser.parse_args()  # pylint: disable=C0103
    DOMAIN = getattr(args, 'project')
    app.run(debug=True, threaded=True)
