#!/usr/bin/env python
# manage.py: application management for flask-form-demo
# Copyright 2014 Sudaraka Wijesinghe <sudaraka.org/contact>
# All rights Reserved.
#

""" flask-form-demo """

import json
import datetime

from flask import Flask, render_template, redirect, request

from flask.ext.script import Manager, Server as ServerCommand
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data.sqlite3'

manager = Manager(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

user_form_list = [
    {'name': 'User 1', 'form_key': 'test'},
    {'name': 'User 2', 'form_key': '83285p2u'},
    {'name': 'User 3', 'form_key': 'l6l8ma54'},
    {'name': 'User 4', 'form_key': '9fs79v3u'},
    {'name': 'User 5', 'form_key': 'k4n3cv92'},
]


class Server(ServerCommand):
    """ Server command handler """

    def handle(self, *args, **kwargs):
        """ handle """

        app.running = True

        super(Server, self).handle(*args, **kwargs)

        print("Shutting down...")
        app.running = False


manager.add_command('runserver', Server)


class FormData(db.Model):
    """ FormData model """

    __tablename__ = 'form_data'

    id = db.Column(db.Integer, primary_key=True)
    form_key = db.Column(db.String(32))
    data = db.Column(db.Text())
    saved_time = db.Column(db.DateTime())


def check_form_key(key):
    """ check if form key is valid """

    keys = [k['form_key'] for k in user_form_list if k['form_key'] == key]

    return 0 < len(keys)


@app.route('/')
def homepage():
    """ homepage """

    form_data = FormData()

    return render_template('index.html', user_list=user_form_list,
                           form_data=form_data.query.all())


@app.route('/form/<string:form_key>')
def form(form_key):
    """ render the form template """

    if not check_form_key(form_key):
        return redirect('/')

    return render_template('form.html', form_key=form_key)


@app.route('/form/<string:form_key>/save', methods=['POST'])
def save_form(form_key):
    """ save form and redirect to confirmation page """

    if not check_form_key(form_key):
        return redirect('/')

    form_data = FormData()
    form_data.data = json.dumps(request.form)
    form_data.form_key = form_key
    form_data.saved_time = datetime.datetime.now()

    db.session.add(form_data)
    db.session.commit()

    return redirect('/form/%s/done' % form_key)


@app.route('/form/<string:form_key>/done')
def form_done(form_key):
    """ render the submit result template """

    if not check_form_key(form_key):
        return redirect('/')

    return render_template('result.html', form_key=form_key)


if '__main__' == __name__:
    manager.run()
