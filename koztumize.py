#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Kozea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
The file which launch the Koztumize application.

"""

from brigit import Git, GitException
import os
import mimetypes
from weasy.document import PDFDocument
from copy import deepcopy
import argparse
import docutils.core
from HTMLParser import HTMLParser
from flask import (
    Flask, request, render_template, send_file, url_for,
    g, redirect, flash, session, current_app, Response, send_from_directory)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive, roles
from tempfile import NamedTemporaryFile
from log_colorizer import make_colored_stream_handler
from logging import getLogger
from functools import wraps
import logging
import ldap
import model as db_model
import csstyle
from datetime import datetime


HANDLER = make_colored_stream_handler()
getLogger('brigit').addHandler(HANDLER)
getLogger('werkzeug').addHandler(HANDLER)
getLogger('werkzeug').setLevel(logging.INFO)
getLogger('brigit').setLevel(logging.DEBUG)
getLogger('WEASYPRINT').setLevel(logging.INFO)
getLogger('WEASYPRINT').addHandler(logging.StreamHandler())

mimetypes.add_type("image/svg+xml", "svg")


class Koztumize(Flask):
    """The class which open the ldap."""
    @property
    def ldap(self):
        """Open the ldap."""
        if 'LDAP' not in self.config:  # pragma: no cover
            self.config['LDAP'] = ldap.open(self.config['LDAP_HOST'])
        return self.config['LDAP']

app = Koztumize(__name__)  # pylint: disable=C0103
format = '%Y-%m-%d %H:%M:%S'


@app.route('/login', methods=('POST',))
def login():
    """This function is called to check if a username /
    password combination is valid against the LDAP.

    """
    username = request.form['login']
    password = request.form['passwd']
    user = current_app.ldap.search_s(
        app.config['LDAP_PATH'], ldap.SCOPE_ONELEVEL, "uid=%s" % username)
    if not user or not password:
        flash(u"Erreur : Les identifiants sont incorrects.", 'error')
        return render_template('login.html')
    try:
        current_app.ldap.simple_bind_s(user[0][0], password)
    except ldap.INVALID_CREDENTIALS:  # pragma: no cover
        flash(u"Erreur : Les identifiants sont incorrects.", 'error')
        return render_template('login.html')
    session["user"] = user[0][1]['cn'][0].decode('utf-8')
    session["usermail"] = user[0][1].get('mail', ["none"])[0].decode('utf-8')
    return redirect(url_for('index'))


def auth(func):
    """Check if the user is logged in, ask for authentication instead."""
    @wraps(func)
    def auth_func(*args, **kwargs):
        """Decorator of the auth function."""
        if session.get('user'):
            return func(*args, **kwargs)
        else:
            return render_template('login.html')
    return auth_func


@app.before_request
def before_request():
    """Set variables before each request."""
    g.domain = app.config['DOMAIN'] or request.host.split('.')[0]
    g.git_archive = Git(app.config['ARCHIVE'])
    g.git_model = Git(os.path.join(app.config['MODEL'], g.domain))


@app.route('/', methods=('GET',))
@auth
def index():
    """This is the route where you choose the model you want to edit."""
    path_model = os.path.join(app.config['MODEL'], g.domain, 'model')
    models = {
        category: os.listdir(os.path.join(path_model, category))
        for category in os.listdir(path_model)}
    print request.args.get('author_select')

    authors_query = db_model.DB.session.query(
        db_model.GitCommit.author_name.label('author_name')).distinct()
    authors = []
    for author in authors_query:
        authors.append({'author_name': author.author_name})
    return render_template('new.html', models=models, authors=authors)


@app.route('/history/get/', methods=('GET',))
@app.route('/history/get/<author>', methods=('GET',))
@auth
def history_get(author=None):
    """This is the route where the commit history is done."""
    history_query = db_model.GitCommit.query.filter(
        db_model.GitCommit.message.like(
            'Modify ' + app.config['DOMAIN'] + '%'))
    if author:
        history_query = history_query.filter(
                db_model.GitCommit.author_name == author)
    history = []
    for hist in history_query.limit(10).all():
        history.append({
            'author_name': hist.author_name,
            'author_email': hist.author_email,
            'commit': hist.commit[:7],
            'message': hist.message.rsplit('/')[-1],
            'date':  hist.date.strftime(
                "le %d/%m/%Y à %H:%M:%S").decode('utf-8'),
            'link': hist.message[7:]})
    return render_template('new_ajax.html', history=history)


@app.route('/generate', methods=('POST',))
@auth
def generate():
    """
    The route where the .PDF document is made with the given HTML. /
    The PDF is returned to the client.

    """
    document = PDFDocument.from_string(request.form['html_content'])
    temp_file = NamedTemporaryFile(suffix='.pdf', delete=True)
    document.write_to(temp_file)
    return send_file(temp_file.name, as_attachment=True,
                     attachment_filename=request
                     .form['filename'][:-4] + '.pdf')


@app.route('/archive')
@app.route('/archive/<path:path>')
@auth
def archive(path=''):
    """The route where you can access your archived files."""
    g.git_archive.checkout('master')
    archived_dirs = []
    archived_files = []
    for element in os.listdir(os.path.join(app.config['ARCHIVE'], path)):
        if os.path.isdir(os.path.join(app.config['ARCHIVE'], path, element)):
            if not element.startswith("."):
                archived_dirs.append(os.path.join(path, element))
        else:
            archived_files.append(os.path.join(path, element))
    return render_template('archive.html', archived_dirs=archived_dirs,
                           archived_files=archived_files, path=path)


@app.route('/archive_get', methods=('GET',))
@auth
def archive_get():
    """This is the route where you can get the archives by name."""
    return render_template('archive_ajax.html',
                           filename=request.form['search'])


@app.route('/modify/<path:path>')
@app.route('/modify/<path:path>/<version>')
@auth
def modify(path, version=''):
    """This is the route where you can modify your models."""
    file_path = os.path.join(app.config['ARCHIVE'], path)

    g.git_archive.checkout('master')
    hist = list(g.git_archive.pretty_log(file_path))

    g.git_archive.checkout("%s" % version)
    parser = ModelParser()
    parser.feed(open(file_path).read())
    path_model = parser.model
    date_model = parser.date
    g.git_model.checkout('master@{%s}' % date_model)
    date_commit = []
    for commit in range(len(hist)):
        date_commit.append(
            {'date': hist[commit]['datetime']
             .strftime("le %d/%m/%Y à %H:%M:%S").decode('utf-8'),
             'commit': hist[commit]['hash'][:7],
             'author': hist[commit]['author']['name']})
    category, filename = path_model.rsplit('/', 1)
    today = datetime.today().strftime(format)
    return render_template('modify.html', category=category,
                           filename=filename, date_commit=date_commit,
                           path=path, date=today)


@app.route('/file/<path:path>')
@auth
def reader(path):
    """The route which read the archived .html."""
    file_content = open(os.path.join(app.config['ARCHIVE'], path)).read()
    return file_content


@app.route('/save', methods=('POST',))
@auth
def save():
    """This is the route where you can edit save your changes."""
    edited_file = request.form['filename'] + '.html'
    path_domain = os.path.join(os.path.join(
        g.git_archive.path, g.domain))
    if os.path.exists(path_domain):
        g.git_archive.checkout("master")
        g.git_archive.pull()
    path_category = os.path.join(path_domain, request.form['category'])
    path_file = os.path.join(path_category, edited_file)
    path_message = os.path.join(
        g.domain, request.form['category'], edited_file)
    if not os.path.exists(path_domain):  # pragma: no cover
        os.mkdir(path_domain)
    if not os.path.exists(path_category):  # pragma: no cover
        os.mkdir(path_category)
    if os.path.exists(path_domain):
        g.git_archive.pull()
    open(path_file, 'w').write(request.form['html_content'].encode("utf-8"))
    open(path_file, "a+").close()
    g.git_archive.add(".")
    try:
        g.git_archive.commit(
            u"--author=%s <%s>'" % (session['user'], session['usermail']),
            message=u"Modify %s" % path_message)
    except GitException:  # pragma: no cover
        flash(u"Erreur : Le fichier n'a pas été modifié.", 'error')
    else:
        g.git_archive.push("origin", "master")
        flash(u"Enregistrement effectué.", 'ok')

    return redirect(url_for('modify',
                            path=os.path.join(g.domain,
                                              request.form['category'],
                                              edited_file), version='master'))


@app.route('/edit/<category>/<filename>')
@auth
def edit(category, filename):
    """This is the route where you can edit the models."""
    return render_template('base.html', category=category, filename=filename)


@app.route('/model/<category>/<filename>')
@auth
def model(category, filename):
    """This is the route that returns the model."""
    g.git_model.checkout("master")
    path_file = os.path.join(app.config['MODEL'],
                             g.domain, 'model', category, filename)
    source = open(path_file).read().decode("utf-8") + u"""

.. meta::
   :model: %s/%s""" % (category, filename) + u"""
   :date: %s""" % (datetime.today().strftime(format))

    dom_tree = docutils.core.publish_doctree(source=source).asdom()
    list_field = dom_tree.getElementsByTagName('field')
    for field in list_field:
        if (field.childNodes.item(0).childNodes.item(0).nodeValue ==
            'stylesheet'):
            stylesheets = (
                field.childNodes.item(1).childNodes.item(0)
                .childNodes.item(0).nodeValue)
    arguments = {
        'stylesheet': url_for('stylesheet', path=os.path.join(
            stylesheets), _external=True),
        'stylesheet_path': None,
        'embed_stylesheet': False}
    parts = docutils.core.publish_parts(
        source=source, writer=Writer(), settings_overrides=arguments)
    text = parts['whole']
    return text


@app.route('/model_static/<path:path>.css')
def stylesheet(path):
    """CSS stylesheet created by CSStyle."""
    filename = os.path.join(
        app.config['MODEL'], g.domain, 'model_styles', path + '.css')
    parser = csstyle.Parser([filename])
    text = '/* Generated by CSStyle */\n\n'
    text += repr(parser)
    for engine in csstyle.BROWSERS:
        browser_parser = getattr(csstyle, engine)
        text += '\n\n/* CSS for %s */\n\n' % engine
        text += repr(browser_parser.transform(
            deepcopy(parser), keep_existant=False))
    return Response(text, mimetype='text/css')


@app.route('/model_static/<path:path>')
def model_static(path):
    """Return files from the model directory."""
    return send_from_directory(os.path.join(
        app.config['MODEL'], g.domain, 'model_styles'), path, cache_timeout=0)


@app.route('/logout')
@auth
def logout():
    """This is the route where the user can log out."""
    session.pop('user')
    session.pop('usermail')
    return render_template('login.html')


class ModelParser(HTMLParser):
    """A class which parse the HTML from the model."""
    def __init__(self):
        self.model = ''
        self.date = ''
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            meta = dict(attrs)
            if meta.get('name') == "model":
                self.model = meta['content']
            if meta.get('name') == "date":
                self.date = meta['content']


class Editable(Directive):
    """A rest directive which creates an editable div in HTML."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False
    option_spec = {'class': directives.class_option,
                   'id': directives.class_option}

    def run(self):
        content = (
        '<div contenteditable="true" class="%s" id="%s" title="%s"></div>' % (
            ' '.join(self.options.get('class', [])),
            ' '.join(self.options.get('id', [])),
            self.arguments[0] if self.arguments else ''))
        return [docutils.nodes.raw('', content, format='html')]


# The signature of this function is given by docutils
# pylint: disable=R0913,W0613
def editable(name, rawtext, text, lineno, inliner, options=None,
             content=None):
    """."""
    content = '<span contenteditable="true">%s</span>' % text
    return [docutils.nodes.raw('', content, format='html')], []
# pylint: enable=R0913,W0613

roles.register_canonical_role('editable', editable)


class Script(Directive):
    """A rest directive which creates a script tag in HTML."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        path = url_for('model_static', path=os.path.join(
            'javascript', '%s.js') % (
                self.arguments[0] if self.arguments else ''), _external=True)
        content = ('<script src="%s" type="text/javascript"></script>' % path)
        return [docutils.nodes.raw('', content, format='html')]


class Button(Directive):
    """A rest directive who create a button in HTML."""
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {'class': directives.class_option}

    def run(self):
        content = ('<input type="button" class="%s" value="%s" onclick="%s"/>'
                  % (
                      ' '.join(self.options.get('class', [])),
                      self.arguments[0], self.arguments[1],
                  ))
        return [docutils.nodes.raw('', content, format='html')]


class JQuery(Directive):
    """A rest directive which includes JQuery."""
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = ('<script src="http://code.jquery.com/jquery.min.js"\
                   type="text/javascript"></script>')
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
directives.register_directive('script', Script)
directives.register_directive('jquery', JQuery)
directives.register_directive('button', Button)

app.secret_key = 'MNOPQR'

if __name__ == '__main__':  # pragma: no cover
    arg_parser = argparse.ArgumentParser()  # pylint: disable=C0103
    arg_parser.add_argument(
        '-c', '--config',
        default='config_default.py',
        help='Choose your config file')
    parser_args = arg_parser.parse_args()  # pylint: disable=C0103
    CONFIG_FILE = getattr(parser_args, 'config')
    if CONFIG_FILE:
        app.config.from_pyfile(CONFIG_FILE)
    db_model.init(app)
    app.run(debug=True, threaded=True)
