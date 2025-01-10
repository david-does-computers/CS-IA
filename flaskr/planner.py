from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db
from datetime import datetime

bp = Blueprint('task', __name__)

@bp.route('/')
def index():
    db = get_db()
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    tasks = db.execute(
        'SELECT task_id, title, description, category, priority, due_date, completed, created_at, u.username'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY due_date, priority DESC',
        (g.user['id'],)
    ).fetchall()

    active_tasks = []
    completed_tasks = []
    for i in range(len(tasks)):
        task = dict(tasks[i])
        due_date = task['due_date']
        days_remaining = (due_date - datetime.today().date()).days
        task['days_remaining'] = days_remaining
        if task['completed']:
            completed_tasks.insert(0, task)
        else:
            active_tasks.append(task)

    print(completed_tasks)

    return render_template('task/index.html', active_tasks=task_sort(active_tasks), completed_tasks=completed_tasks[:10])

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
                ' WHERE task_id = ?',
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




def task_sort(tasks):
    # Calculate the urgency score for each task based on priority and days remaining
    urgency_scores = [task['priority'] / (task['days_remaining'] + 1) for task in tasks]

    # Bubble sort based on the score to have the most urgent tasks first
    for i in range(len(tasks)-1):
        for j in range(len(tasks)-i-1):
            if urgency_scores[i] < urgency_scores[i+1]:
                temp = tasks[i] 
                tasks[i] = tasks[i+1]
                tasks[i+1] = temp

                temp = urgency_scores[i]
                urgency_scores[i] = urgency_scores[i+1]
                urgency_scores[i+1] = temp
    return tasks


