import os
import logging
import re
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, session
from flask_socketio import SocketIO

try:
    from flask_cors import CORS
except ImportError:
    def CORS(app): return None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(): return False

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='app/static')
secret_key = os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing. Add it to backend/.env before starting the app.")
app.secret_key = secret_key
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

PORT = int(os.environ.get("PORT", "5001"))

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
gemini_client = None

if api_key and genai is not None:
    try:
        gemini_client = genai.Client(api_key=api_key)
        logging.info("Google Gemini AI Engine linked successfully.")
    except Exception as err:
        logging.error(f"Gemini SDK failure: {str(err)}")
else:
    logging.warning("No GEMINI_API_KEY or GOOGLE_API_KEY found. The chatbot will return simulation responses until a valid key is set.")

class EnterpriseWarningMatrix:
    def __init__(self):
        self.baseline_historical_expenses = 20000.0

    def generate_year_schedule(self, plan_type, current_data):
        schedule_items = []
        start_date = datetime.now()

        phases = [
            {"phase_name": "Immediate Stabilization", "focus_area": "Expense Mitigation", "action_metric": "Cut Overhead"},
            {"phase_name": "Cash Flow Optimization", "focus_area": "Invoice Acceleration", "action_metric": "Collect AR"},
            {"phase_name": "Growth Transition", "focus_area": "Marketing Channels", "action_metric": "Acquire Leads"},
            {"phase_name": "Scale Operations", "focus_area": "Digital Automation", "action_metric": "Maximize Margin"}
        ]

        iterations = 365 if plan_type == 'daily' else 12
        for idx in range(iterations):
            if plan_type == 'daily':
                current_date = start_date + timedelta(days=idx)
                phase_assigned = phases[min(idx // 92, len(phases) - 1)]
                date_str = current_date.strftime("%b %d")
                day_lbl = current_date.strftime("%a")
                title = f"Day {idx + 1}: {phase_assigned['phase_name']}"
                badge = "Daily Task"
            else:
                current_date = start_date + timedelta(days=idx * 30.5)
                phase_assigned = phases[min(idx // 3, len(phases) - 1)]
                date_str = current_date.strftime("%B")
                day_lbl = f"M {idx + 1}"
                title = f"Strategic Directive {idx + 1}"
                badge = "Monthly Milestone"

            status_state = "Overdue" if idx < 3 else "Pending"

            schedule_items.append({
                "id": f"task_{idx + 1}",
                "date_string": date_str,
                "day_label": day_lbl,
                "title": title,
                "category": phase_assigned['focus_area'],
                "badge_text": badge,
                "status": status_state,
                "description": f"Execute operations targeting objective: {phase_assigned['action_metric']}."
            })
        return schedule_items

    def compute_matrix(self, payload):
        try:
            revenue = float(payload.get('revenue', 18000) or 0)
            expenses = float(payload.get('expenses', 21000) or 0)
            cash = float(payload.get('cash_reserves', 35000) or 0)
            growth = float(payload.get('growth_rate', 3.2) or 0)
            plan_type = payload.get('plan_type', 'daily')

            net_burn = expenses - revenue
            is_profitable = net_burn <= 0

            if is_profitable:
                runway_display = "Infinite (Profitable)"
                runway_status = "green"
            else:
                runway_months = round(cash / net_burn, 1) if net_burn > 0 else 99
                runway_display = f"{runway_months} Months"
                runway_status = "red" if runway_months <= 6.0 else "green"

            final_risk = 15.0 if is_profitable else min(100.0, 30.0 + (expenses / max(1.0, revenue)) * 20.0)

            base_matrix = {
                "username": session.get('username', 'Founder'),
                "raw_revenue": revenue,
                "raw_expenses": expenses,
                "revenue": f"${revenue:,.2f}",
                "expenses": f"${expenses:,.2f}",
                "cash_runway": runway_display,
                "growth_rate": f"{growth:.1f}%", 
                "risk_score": f"{final_risk:.0f}%",
                "plan_type": plan_type,
                "status_indicators": {
                    "performance": "green" if is_profitable else "red",
                    "runway": runway_status,
                    "growth": "green" if growth >= 0 else "red",
                    "risk": "red" if final_risk >= 50.0 else "green"
                }
            }
            base_matrix["playbook_tasks"] = self.generate_year_schedule(plan_type, base_matrix)
            return base_matrix
        except Exception as err:
            logging.error(f"Computation failure: {err}")
            return {"error": "Invalid metrics processing."}

matrix_engine = EnterpriseWarningMatrix()

@app.route('/')
def home(): return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            return redirect('/setup')
        return render_template('login.html', error=True)
    return render_template('login.html', error=None)

@app.route('/setup', methods=['GET', 'POST'])
def setup_telemetry():
    if request.method == 'POST':
        payload = {
            'revenue': request.form.get('revenue', 19500),
            'expenses': request.form.get('expenses', 22000),
            'cash_reserves': request.form.get('cash_reserves', 45000),
            'growth_rate': request.form.get('growth_rate', 4.5),
            'plan_type': request.form.get('plan_type', 'daily')
        }
        session['active_matrix'] = matrix_engine.compute_matrix(payload)
        return redirect('/dashboard')
    return render_template('setup.html')

@app.route('/dashboard')
def dashboard():
    matrix_data = session.get('active_matrix', None)
    if not matrix_data: return redirect('/setup')
    return render_template('index.html', matrix=matrix_data)

@app.route('/api/v1/telemetry/recalculate', methods=['POST'])
def recalculate_live():
    """NEW FEATURE backend route to allow sliding adjustments without switching screens."""
    payload = request.get_json() or {}
    matrix_output = matrix_engine.compute_matrix(payload)
    session['active_matrix'] = matrix_output
    return jsonify(matrix_output), 200

@app.route('/api/v1/tasks/toggle', methods=['POST'])
def toggle_task_status():
    payload = request.get_json() or {}
    task_id = payload.get('task_id')
    matrix_data = session.get('active_matrix', None)
    if not matrix_data or not task_id: return jsonify({"error": "Missing parameters"}), 400

    for task in matrix_data.get('playbook_tasks', []):
        if task['id'] == task_id:
            task['status'] = "Completed" if task['status'] != "Completed" else "Pending"
            session['active_matrix'] = matrix_data
            return jsonify({"success": True, "new_status": task['status']}), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/api/v1/chat', methods=['POST'])
def chatbot_api():
    payload = request.get_json() or {}
    user_msg = payload.get('message', '')
    if not gemini_client: return jsonify({"reply": "• Operating under local simulation configuration parameters."}), 200
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', contents=user_msg,
            config=types.GenerateContentConfig(system_instruction="Be an encouraging short business advisor.", temperature=0.3)
        )
        return jsonify({"reply": response.text or "Acknowledged."}), 200
    except: return jsonify({"reply": "API link timeout."}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True)