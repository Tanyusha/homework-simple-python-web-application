from __future__ import unicode_literals, print_function, generators, division
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

__author__ = 'Tanika'


# configuration
DATABASE = 'Flask_Home_Work.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

print(__name__)


# @app.route('/', defaults={'name': 'Flask'})
# @app.route('/<name>')
# def index(name):
#     return render_template('index.html', name=name)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_complains():
    session.pop('log', None)
    # session.pop('user', None)
    cur = g.db.execute('select title, text, user from entries order by id desc')
    complains = [dict(title=row[0], text=row[1], user=row[2]) for row in cur.fetchall()]
    return render_template('show_complains.html', complains=complains)

@app.route('/add', methods=['POST'])
def add_complain():
    # if not session.get('logged_in'):
    #     abort(401)
    print('fff')
    print(session['user'])
    g.db.execute('insert into entries (title, text, user) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], session['user']])
    g.db.commit()
    flash('Новая жалоба успешно добавлена')
    return redirect(url_for('show_complains'))


@app.route('/check_in', methods=['GET', 'POST'])
def check_in():
    error = None
    if request.method == 'POST':
        if request.form['password'] != request.form['password-2']:
            error = 'Пароли не совпадают'
        else:
            try:
                g.db.execute('insert into users (user, password) values (?, ?)',
                             [request.form['username'], request.form['password']])
            except Exception as e:
                print(e)
                error = "Пользователь с таким именем уже существует"
            g.db.commit()
            session['user'] = request.form['username']
            flash(session['user'])
            return redirect(url_for('show_complains'))
    return render_template('check_in.html', error=error)
    # g.db.execute('insert into users (user, password) values (?, ?)',
    #              [request.form['user'], request.form['password']])
    # g.db.commit()
    # return redirect(url_for('show_complains'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            print(request.form['username'])
            cur = g.db.execute('select * from users where user = ?',
                               [request.form['username']])
        except Exception as e:
            print(e)
        else:
            user = [dict(user=row[1], password=row[2]) for row in cur.fetchall()]
            print(user)
            if not user:
                error = "Пользоваетеля с таким именем не существует"
                print(error)
            else:
                if user[0]['password'] != request.form['password']:
                    error = 'Неверный пароль'
                else:
                    session['user'] = request.form['username']
                    return redirect(url_for('show_complains'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('log', None)
    session.pop('user', None)
    flash('Вы вышли из системы')
    return redirect(url_for('show_complains'))


if __name__ == "__main__":
    app.run()