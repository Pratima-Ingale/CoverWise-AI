from flask import Blueprint, render_template

view_bp = Blueprint('views', __name__)

@view_bp.route('/')
def home():
    """Renders the Home landing page."""
    return render_template('index.html')

@view_bp.route('/input')
def customer_input():
    """Renders the Customer Input form page."""
    return render_template('input.html')

@view_bp.route('/recommendations')
def recommendations():
    """Renders the Policy Recommendations page."""
    return render_template('recommendations.html')

@view_bp.route('/compare')
def compare():
    """Renders the Policy Comparison page."""
    return render_template('compare.html')
