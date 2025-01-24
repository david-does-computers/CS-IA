import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from src.db import get_db

bp = Blueprint('session', __name__, url_prefix='/session')

@bp.route('/')
def index():
    return render_template('session/index.html')
