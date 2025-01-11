import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                user_id = db.execute(
                    "SELECT id FROM user WHERE username = ?",
                    (username,)
                ).fetchone()["id"]


                # Pre-add entries to category table for the new user
                db.execute(
                    "INSERT INTO category (name, user_id) VALUES (?, ?)",
                    ("Assignment", user_id),
                )
                db.execute(
                    "INSERT INTO category (name, user_id) VALUES (?, ?)",
                    ("Test Review", user_id),
                )
                db.execute(
                    "INSERT INTO category (name, user_id) VALUES (?, ?)",
                    ("Misc.", user_id),
                )
                db.commit()
            except db.IntegrityError as e:
                if "UNIQUE constraint failed: user.username" in str(e):
                    error = f"User {username} is already registered."
                elif "CHECK constraint failed: length(username) <= 15" in str(e):
                    error = "Username must be 15 characters or fewer."
                else:
                    error = "An error occurred. Please try again."
                    print(e)

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view