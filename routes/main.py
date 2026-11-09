from flask import Blueprint, render_template
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template(
        'index.html',
        free_limit=Config.FREE_TIER_DAILY_LIMIT
    )

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
