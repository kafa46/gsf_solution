from flask import Blueprint, render_template, request

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template(
        "index.html"
    )
    
@bp.route('/monitor/')
def monitor():
    return render_template(
        'monitor.html'
    )
    
@bp.route('/setting/')
def setting():
    return render_template(
        'setting.html'
    )
