#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
The file which launch the Koztumize application.

"""

from brigit import Git, GitException
import os
import weasy
import argparse
import docutils.core
from HTMLParser import HTMLParser
from flask import (
    Flask, request, render_template, send_file, url_for,
    g, redirect, flash, session, current_app)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive
from tempfile import NamedTemporaryFile
from log_colorizer import make_colored_stream_handler
from logging import getLogger
from functools import wraps
import logging
import ldap
import model as db_model


HANDLER = make_colored_stream_handler()
getLogger('brigit').addHandler(HANDLER)
getLogger('werkzeug').addHandler(HANDLER)
getLogger('werkzeug').setLevel(logging.INFO)
getLogger('brigit').setLevel(logging.DEBUG)


class Koztumize(Flask):
    @property
    def ldap(self):
        if 'LDAP' not in self.config:
            self.config['LDAP'] = ldap.open(self.config['LDAP_HOST'])
        return self.config['LDAP']

app = Koztumize(__name__)  # pylint: disable=C0103


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
    except ldap.INVALID_CREDENTIALS:
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
    g.git = Git(os.path.join(app.config['ARCHIVE'], g.domain))


@app.route('/', methods=('GET',))
@auth
def index():
    """This is the route where you choose the model you want to edit."""
    path_model = os.path.join('static', 'domain', g.domain, 'model')
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
        db_model.GitCommit.message.like('Modify ' + app.config['DOMAIN'] + '%'))
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
    document = weasy.PDFDocument.from_string(request.form['html_content'])
    temp_file = NamedTemporaryFile(suffix='.pdf', delete=True)
    document.write_to(temp_file)
    return send_file(temp_file.name, as_attachment=True,
                     attachment_filename=request.form['filename'] + '.pdf')


@app.route('/archive')
@app.route('/archive/<path:path>')
@auth
def archive(path=''):
    """The route where you can access your archived files."""
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


@app.route('/modify/<path:path>')
@app.route('/modify/<path:path>/<version>')
@auth
def modify(path, version=''):
    """This is the route where you can modify your models."""
    file_path = os.path.join(app.config['ARCHIVE'], path)
    g.git.checkout("master")
    hist = list(g.git.pretty_log(file_path))
    g.git.checkout("%s" % version)
    date_commit = []
    for commit in range(len(hist)):
        date_commit.append(
            {'date': hist[commit]['datetime']
             .strftime("le %d/%m/%Y à %H:%M:%S").decode('utf-8'),
             'commit': hist[commit]['hash'][:7],
             'author': hist[commit]['author']['name']})
    parser = ModelParser()
    parser.feed(open(file_path).read())
    path_model = parser.result
    category, filename = path_model.rsplit('/', 1)
    return render_template('modify.html', category=category,
                           filename=filename, date_commit=date_commit,
                           path=path)


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
    g.git.checkout("master")
    edited_file = request.form['filename'][:-4] + '.html'
    path_domain = os.path.join(g.git.path)
    path_category = os.path.join(path_domain, request.form['category'])
    path_file = os.path.join(path_category, edited_file)
    path_message = os.path.join(
        g.domain, request.form['category'], edited_file)
    if not os.path.exists(path_domain):  # pragma: no cover
        os.mkdir(path_domain)
    if not os.path.exists(path_category):  # pragma: no cover
        os.mkdir(path_category)
    open(path_file, 'w').write(request.form['html_content'].encode("utf-8"))
    open(path_file, "a+").close()
    g.git.add(".")
    try:
        g.git.commit(
            u"--author=%s <%s>'" % (session['user'], session['usermail']),
            message=u"Modify %s" % path_message)
    except GitException:
        flash(u"Erreur : Le fichier n'a pas été modifié.", 'error')
    else:
        g.git.push()
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
    path_file = os.path.join('static', 'domain',
                             g.domain, 'model', category, filename)
    stylesheet = ''
    source = open(path_file).read().decode("utf-8") + u"""

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
        self.result = ''
        HTMLParser.__init__(self)

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
    arg_parser.add_argument(
        '-c', '--config',
        default='config_default.py',
        help='Choose your config file')
    args = arg_parser.parse_args()  # pylint: disable=C0103
    CONFIG_FILE = getattr(args, 'config')
    if CONFIG_FILE:
        app.config.from_pyfile(CONFIG_FILE)
    db_model.init(app)
    app.run(debug=True, threaded=True)
