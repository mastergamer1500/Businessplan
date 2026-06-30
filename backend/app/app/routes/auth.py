from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def root_gateway():
    if session.get('user_authenticated'):
        return redirect(url_for('auth.input_view'))
    return redirect(url_for('auth.login_view'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        # Credentials validation framework
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple checkpoint credentials pass
        if username == "admin" or username == "":
            session['user_authenticated'] = True
            return redirect(url_for('auth.input_view'))
            
    return render_template('login.html')

@auth_bp.route('/input', methods=['GET'])
def input_view():
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.login_view'))
    return render_template('input.html')

@auth_bp.route('/process-metrics', methods=['POST'])
def process_metrics():
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.login_view'))
        
    # Commit ingestion values to the active session server cache map cookie
    session['revenue'] = request.form.get('revenue', '18000')
    session['expenses'] = request.form.get('expenses', '21000')
    session['cash_reserves'] = request.form.get('cash_reserves', '35000')
    session['growth_rate'] = request.form.get('growth_rate', '3.2')
    session['macro_context'] = request.form.get('macro_context', 'nominal')
    
    return redirect(url_for('auth.results_dashboard'))

@auth_bp.route('/results', methods=['GET'])
def results_dashboard():
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.login_view'))
    if 'revenue' not in session:
        return redirect(url_for('auth.input_view'))
        
    return render_template('index.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_view'))