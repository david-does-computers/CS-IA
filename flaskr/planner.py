from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db

bp = Blueprint('task', __name__)

@bp.route('/')
def index():
    db = get_db()
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    tasks = db.execute(
        'SELECT task_id, title, description, category, priority, due_date, completed, created_at, u.username'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE completed = FALSE AND u.id = ?'
        ' ORDER BY due_date, priority DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('task/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        priority = request.form['priority']
        due_date = request.form['due_date']
        error = None

        if not (title or category or due_date):
            error = 'Missing details.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (title, description, category, priority, due_date, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (title, description, category, priority, due_date, g.user['id'])
            )
            db.commit()
            return redirect(url_for('task.index'))

    return render_template('task/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        priority = request.form['priority']
        due_date = request.form['due_date']
        completed = request.form.get('completed') == 'on'
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET title = ?, description = ?, category = ?, priority = ?, due_date = ?, completed = ?'
                ' WHERE id = ?',
                (title, description, category, priority, due_date, completed, id)
            )
            db.commit()
            return redirect(url_for('task.index'))

    return render_template('task/update.html', task=task)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    print("Deleting task", id)
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM task WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('task.index'))

def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT task_id, title, description, category, priority, due_date, completed, created_at, user_id, u.username'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE task_id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and task['user_id'] != g.user['id']:
        abort(403)

    return task

@bp.route('/<int:id>/complete', methods=('POST',))
@login_required
def complete_task(id):
    task = get_task(id)
    db = get_db()
    db.execute('UPDATE task SET completed = TRUE WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('task.index'))