#!/usr/bin/env python2

from flask import (
    Flask, request, render_template, send_file)
from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import directives, Directive
import docutils.core
import os
import weasy
import cssutils


app = Flask(__name__)  # pylint: disable=C0103


@app.route('/')
def index():
    html = request.args.get('html')

    if html:
        document = weasy.PDFDocument.from_string(
            html, user_stylesheets=[
                cssutils.parseFile('static/model.css')])
        document.write_to('tmp/result.pdf')
        return send_file('tmp/result.pdf')
    else:
        models = {
            category: os.listdir('static/model/' + category)
            for category in os.listdir('static/model')}
        return render_template('index.html', models=models)


@app.route('/edit/<category>/<filename>')
def edit(category, filename):
    return render_template('base.html', category=category, filename=filename)


@app.route('/model/<category>/<filename>')
def model(category, filename):
    return rest_to_html(category, filename)


def rest_to_html(category, filename):
    args = {'stylesheet_path': 'static/style.css'}
    parts = docutils.core.publish_parts(
        source=open(os.path.join(
            'static', 'model', category, filename + '.rst')).read(),
        writer=Writer(), settings_overrides=args)
    text = parts['whole']
    return text


class Editable(Directive):
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        content = '''
            <div contenteditable="true" class="editable"
                 onclick="if(this.innerHTML==\'%s\')this.innerHTML=\'\'">
              %s
            </div>''' % (
                self.arguments[0] if self.arguments else '',
                self.arguments[0] if self.arguments else '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('editable', Editable)


if __name__ == '__main__':
    app.secret_key = 'MNOPQR'
    app.run(debug=True)
