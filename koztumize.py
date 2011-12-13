#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""koztumize.py is used to launch the application Koztumize."""


from brigit import Git, GitException
import os
import weasy
import argparse
import docutils.core
from HTMLParser import HTMLParser
from flask import (
    Flask, request, render_template, send_file, url_for, g, redirect, flash)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive
from tempfile import NamedTemporaryFile
from log_colorizer import make_colored_stream_handler
from logging import getLogger
import logging


HANDLER = make_colored_stream_handler()
getLogger('brigit').addHandler(HANDLER)
getLogger('werkzeug').addHandler(HANDLER)
getLogger('werkzeug').setLevel(logging.INFO)
getLogger('brigit').setLevel(logging.DEBUG)

DOMAIN = None
ARCHIVE = os.path.join(os.path.expanduser('~/archive'))
app = Flask(__name__)  # pylint: disable=C0103


@app.before_request
def before_request():
    """Set variables before each request."""
    g.domain = DOMAIN or request.host.split('.')[0]
    g.git = Git(os.path.join(ARCHIVE, g.domain))


@app.route('/')
def index():
    """Index is the main route of the application."""
    return redirect(url_for('new'))


@app.route('/new')
def new():
    """This is the route where you choose the model you want to edit."""
    path_model = os.path.join('static', 'domain', g.domain, 'model')
    models = {
        category: os.listdir(os.path.join(path_model, category))
        for category in os.listdir(path_model)}
    return render_template('new.html', models=models)


@app.route('/generate', methods=('POST',))
def generate():
    """The route where document .PDF is made with the given HTML and
the document is return to the client."""
    document = weasy.PDFDocument.from_string(request.form['html_content'])
    temp_file = NamedTemporaryFile(suffix='.pdf', delete=True)
    document.write_to(temp_file)
    return send_file(temp_file.name, as_attachment=True,
                     attachment_filename=request.form['filename'] + '.pdf')


@app.route('/archive')
@app.route('/archive/<path:path>')
def archive(path=''):
    """Archive."""
    archived_dirs = []
    archived_files = []
    for element in os.listdir(os.path.join(ARCHIVE, path)):
        if os.path.isdir(os.path.join(ARCHIVE, path, element)):
            if element != '.git':
                archived_dirs.append(os.path.join(path, element))
        else:
            archived_files.append(os.path.join(path, element))
    return render_template('archive.html', archived_dirs=archived_dirs,
                           archived_files=archived_files, path=path)


@app.route('/modify/<path:path>')
@app.route('/modify/<path:path>/<int:version>')
def modify(path, version=0):
    """This is the route where you can modify your models."""
    file_path = os.path.join(ARCHIVE, path)
    g.git.checkout("HEAD~%i" % version, file_path)
    hist = list(g.git.pretty_log(file_path))
    date_commit = []
    for commit in range(len(hist)):
        date_commit.append(
            hist[commit]['datetime'].strftime("le %d-%m-%Y a %H:%M:%S"))
    parser = ModelParser()
    parser.feed(open(file_path).read())
    path_model = parser.result
    category, filename = path_model.rsplit('/', 1)
    return render_template('modify.html', category=category,
                           filename=filename, date_commit=date_commit,
                           path=path)


@app.route('/file/<path:path>')
def reader(path):
    """The route which read the archived .html."""
    file_content = open(os.path.join(ARCHIVE, path)).read()
    return file_content


@app.route('/save', methods=('POST',))
def save():
    """This is the route where you can edit save your changes."""

    edited_file = request.form['filename'] + '.html'
    path_domain = os.path.join(g.git.path)
    path_category = os.path.join(path_domain, request.form['category'])
    path_file = os.path.join(path_category, edited_file)
    if not os.path.exists(path_domain):  # pragma: no cover
        os.mkdir(path_domain)
    if not os.path.exists(path_category):  # pragma: no cover
        os.mkdir(path_category)
    open(path_file, 'w').write(request.form['html_content'].encode("utf-8"))
    open(path_file, "a+").close()
    try:
        g.git.add(".")
        g.git.commit(message="Modify " + edited_file)
    except GitException:
        flash(u"Erreur : Le fichier n'a pas été modifié.", 'error')
    else:
        g.git.push()
        flash(u"Enregistrement effectué.", 'ok')   # pragma: no cover

    return redirect(url_for('modify',
                            path=os.path.join(g.domain,
                                              request.form['category'],
                                              edited_file), version=0))


@app.route('/edit/<category>/<filename>')
def edit(category, filename):
    """This is the route where you can edit the models."""
    return render_template('base.html', category=category, filename=filename)


@app.route('/model/<category>/<filename>')
def model(category, filename):
    """This is the route that returns the model."""
    path_file = os.path.join('static', 'domain',
                             g.domain, 'model', category, filename)
    stylesheet = ''
    source = open(path_file + '.rst').read().decode("utf-8") + u"""

.. meta::
   :model: %s/%s""" % (category, filename)
    dom_tree = docutils.core.publish_doctree(source=source).asdom()
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
                                                     'model_styles',
                                                     stylesheet + '.css'),
                              _external=True),
        'stylesheet_path': None,
        'embed_stylesheet': False}
    parts = docutils.core.publish_parts(
        source=source, writer=Writer(), settings_overrides=arguments)
    text = parts['whole']
    return text


class ModelParser(HTMLParser):
    """A class which parse the HTML from the model."""
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            meta = dict(attrs)
            if 'name' in meta.keys():
                if meta['name'] == "model":
                    self.result = meta['content']


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
