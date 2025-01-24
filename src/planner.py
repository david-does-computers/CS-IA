from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db
from datetime import datetime
import math

bp = Blueprint('task', __name__)

@bp.route('/')
def index():
    sort_category = request.args.get('sort_category', default='-1')
    db = get_db()
    
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    if sort_category and sort_category != '-1':
        tasks = db.execute(
            'SELECT task_id, title, description, category_id, priority, due_date, completed, created_at, u.username'
            ' FROM task t JOIN user u ON t.user_id = u.id'
            ' WHERE u.id = ? AND t.category_id = ?'
            ' ORDER BY due_date, priority DESC',
            (g.user['id'], sort_category)
        ).fetchall()
    else:
        tasks = db.execute(
            'SELECT task_id, title, description, category_id, priority, due_date, completed, created_at, u.username'
            ' FROM task t JOIN user u ON t.user_id = u.id'
            ' WHERE u.id = ?'
            ' ORDER BY due_date, priority DESC',
            (g.user['id'],)
        ).fetchall()

    categories = db.execute(
        'SELECT * FROM category c JOIN user u ON c.user_id = u.id'
        ' WHERE u.id = ?',
        (g.user['id'],)
    ).fetchall()

    active_tasks = []
    completed_tasks = []
    for task in tasks:
        task = dict(task)
        due_date = task['due_date']
        days_remaining = (due_date - datetime.today().date()).days
        task['days_remaining'] = days_remaining

        cat_map = {row["category_id"]: row["name"] for row in categories}
        task["cat_name"] = cat_map.get(task["category_id"], "No category")

        if task['completed']:
            completed_tasks.insert(0, task)
        else:
            active_tasks.append(task)

    return render_template(
        'task/index.html',
        active_tasks=task_sort(active_tasks),
        completed_tasks=completed_tasks[:10],
        categories=categories,
        selected_category=sort_category
    )

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print('create req')
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']
        priority = request.form['priority']
        due_date = request.form['due_date']
        new_category = request.form['new_category']
        error = None
        print(category_id, type(category_id))

        if not (title or category_id or due_date):
            error = 'Missing details.'

        print('error', error)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            if category_id == "-1":
                if new_category:
                    db.execute(
                        "INSERT INTO category (name, user_id) VALUES (?, ?)",
                        (new_category, g.user['id']),
                    )
                    category_id = db.execute(
                        "SELECT MAX(category_id) FROM category"
                    ).fetchone()[0]
                else:
                    flash('New Categroy cannot be empty')

            
            db.execute(
                'INSERT INTO task (title, description, category_id, priority, due_date, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (title, description, category_id, priority, due_date, g.user['id'])
            )
            db.commit()
            return redirect(url_for('task.index'))

    db = get_db()
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    categories = db.execute(
        'SELECT * FROM category c JOIN user u ON c.user_id = u.id'
        ' WHERE u.id = ?',
        (g.user['id'],)
    )
    return render_template('task/create.html', categories=categories)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']
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
                'UPDATE task SET title = ?, description = ?, category_id = ?, priority = ?, due_date = ?, completed = ?'
                ' WHERE task_id = ?',
                (title, description, category_id, priority, due_date, completed, id)
            )
            db.commit()
            return redirect(url_for('task.index'))

    db = get_db()
    
    categories = db.execute(
        'SELECT * FROM category c JOIN user u ON c.user_id = u.id'
        ' WHERE u.id = ?',
        (g.user['id'],)
    ).fetchall()
    return render_template('task/update.html', task=task, categories=categories)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM task WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('task.index'))

def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT task_id, title, description, category_id, priority, due_date, completed, created_at, user_id, u.username'
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
    db = get_db()
    db.execute('UPDATE task SET completed = TRUE WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('task.index'))




def task_sort(tasks):
    # Calculate the urgency score for each task based on priority and days remaining
    urgency_scores = [task['priority'] * math.exp(-task['days_remaining']/5) for task in tasks]

    # Bubble sort based on the score to have the most urgent tasks first
    for i in range(len(tasks)-1):
        for j in range(len(tasks)-i-1):
            if urgency_scores[j] < urgency_scores[j+1]:
                temp = tasks[j] 
                tasks[j] = tasks[j+1]
                tasks[j+1] = temp

                temp = urgency_scores[j]
                urgency_scores[j] = urgency_scores[i+1]
                urgency_scores[j+1] = temp
    return tasks
