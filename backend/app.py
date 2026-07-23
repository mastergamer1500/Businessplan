import os
import logging
import re
import json
import sys
import hashlib
from io import StringIO
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
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
    raise RuntimeError("FLASK_SECRET_KEY is missing. Set it in backend/.env locally, or as an environment variable in the Render dashboard.")
app.secret_key = secret_key
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

PORT = int(os.environ.get("PORT", "5005")) 

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
        # Phase 2: Mock historical database for Feature 2 (Anomaly Detection)
        self.historical_transactions = [
            {"amount": 120.0, "vendor": "AWS Cloud"},
            {"amount": 450.0, "vendor": "Office Supplies Inc"},
            {"amount": 2300.0, "vendor": "Bi-Weekly Payroll"},
            {"amount": 85.0, "vendor": "Github Enterprise"},
            {"amount": 110.0, "vendor": "Slack Technologies"},
            {"amount": 2500.0, "vendor": "Monthly Office Rent"}
        ]

    # --- PHASE 2 FEATURE: ANOMALY DETECTION ENGINE ---
    def scan_for_anomalies(self, current_expenses):
        """
        Feature 2: Compares live business spending against historical habits.
        Flags spikes that exceed 3x the average historical baseline transaction.
        """
        if not self.historical_transactions:
            return []
            
        total_hist = sum(t['amount'] for t in self.historical_transactions)
        avg_hist_spend = total_hist / len(self.historical_transactions)
        
        anomalies = []
        # If the user's input expenses dramatically outpace expectations, flag it
        if current_expenses > (avg_hist_spend * 5):
            anomalies.append({
                "severity": "CRITICAL",
                "message": f"Current monthly budget (${current_expenses:,.2f}) deviates drastically from historical benchmark baseline (${avg_hist_spend:,.2f})."
            })
        return anomalies

    # --- PHASE 4 FEATURE: SUPPLY CHAIN & WORKFLOW OPTIMIZER ---
    def generate_supply_chain_tips(self, revenue, expenses, final_risk):
        """Derives operational & supply-chain recommendations from the current burn profile."""
        tips = []

        if expenses > revenue:
            tips.append({
                "type": "Vendor Restructuring",
                "tip": "Transition immediate raw material and vendor orders into Net-30 payment allocations to unlock short-term working capital without cutting order volume."
            })

        if final_risk >= 50.0:
            tips.append({
                "type": "Inventory Right-Sizing",
                "tip": "Shift high-turnover SKUs to just-in-time restocking to reduce carrying costs and free up cash currently tied up in surplus inventory."
            })

        tips.append({
            "type": "Subscription Consolidation",
            "tip": "Audit recurring SaaS and vendor subscriptions for overlapping tools; consolidating redundant licenses typically recovers 5-10% of monthly overhead."
        })
        tips.append({
            "type": "Workflow Automation",
            "tip": "Automate manual invoice reconciliation and purchase-order approval steps to cut administrative overhead and shorten the vendor payment cycle."
        })

        return tips

    # --- PHASE 4 FEATURE: ALTERNATIVE FINANCING CONNECTOR ---
    def generate_alternative_financing(self, runway_status, vitality_index):
        """Evaluates emergency financing eligibility from the current runway and vitality profile."""
        if runway_status == "red" or vitality_index < 45.0:
            return {
                "status": "Qualified for Emergency Matchmaking",
                "options": [
                    {"provider": "Fintech Advance Corp", "mechanism": "Invoice Factoring", "turnaround": "24 Hours"},
                    {"provider": "BridgeCap Partners", "mechanism": "Revenue-Based Advance", "turnaround": "48 Hours"},
                    {"provider": "Harbor Line Capital", "mechanism": "Short-Term Line of Credit", "turnaround": "3-5 Business Days"}
                ]
            }
        return {
            "status": "Not Currently Required — Cash Position Stable",
            "options": []
        }

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

    def compute_vitality_components(self, revenue, expenses, cash, growth, risk_score_value):
        margin_pct = ((revenue - expenses) / revenue * 100.0) if revenue > 0 else -100.0
        margin_score = max(0.0, min(100.0, (margin_pct + 100.0) / 2.0))

        net_burn = expenses - revenue
        runway_months = (cash / net_burn) if net_burn > 0 else 24.0
        runway_score = max(0.0, min(100.0, (runway_months / 24.0) * 100.0))

        growth_score = max(0.0, min(100.0, (growth + 10.0) * 5.0))
        risk_component = max(0.0, min(100.0, 100.0 - risk_score_value))

        return {
            "margin_score": round(margin_score, 1),
            "runway_score": round(runway_score, 1),
            "growth_score": round(growth_score, 1),
            "risk_component": round(risk_component, 1)
        }

    def compute_vitality_index(self, revenue, expenses, cash, growth, risk_score_value):
        c = self.compute_vitality_components(revenue, expenses, cash, growth, risk_score_value)
        index = (0.30 * c["margin_score"]) + (0.25 * c["runway_score"]) + (0.25 * c["growth_score"]) + (0.20 * c["risk_component"])
        return round(index, 1)

    def project_growth_trend(self, revenue, expenses, cash, growth, risk_score_value, months=12):
        monthly_growth_rate = growth / 100.0
        trend_revenue = revenue
        trend_cash = cash

        labels = ["Now"]
        values = [self.compute_vitality_index(trend_revenue, expenses, trend_cash, growth, risk_score_value)]
        revenue_series = [round(trend_revenue, 2)]
        expense_series = [round(expenses, 2)]

        for month_idx in range(1, months + 1):
            trend_revenue *= (1.0 + monthly_growth_rate)
            trend_cash += (trend_revenue - expenses)
            net = trend_revenue - expenses
            projected_risk = 15.0 if net >= 0 else min(100.0, 30.0 + (expenses / max(1.0, trend_revenue)) * 20.0)
            values.append(self.compute_vitality_index(trend_revenue, expenses, trend_cash, growth, projected_risk))
            labels.append(f"M{month_idx}")
            revenue_series.append(round(trend_revenue, 2))
            expense_series.append(round(expenses, 2))

        return labels, values, revenue_series, expense_series

    def compute_matrix(self, payload):
        try:
            # --- PHASE 2 FEATURES: MATHEMATICAL RUNWAY & SANDBOX ENGINE INTEGRATION ---
            raw_revenue = float(payload.get('revenue', 18000) or 0)
            raw_expenses = float(payload.get('expenses', 21000) or 0)
            cash = float(payload.get('cash_reserves', 35000) or 0)
            growth = float(payload.get('growth_rate', 3.2) or 0)
            plan_type = payload.get('plan_type', 'daily')

            # Feature 10 (Sandbox Slider): Read incoming real-world economic supply-chain shock adjustments
            material_price_hike = float(payload.get('material_price_hike', 0) or 0)
            
            # Apply shock mathematically to current expenses instantly
            expenses = raw_expenses * (1.0 + (material_price_hike / 100.0))

            # Feature 3: Mathematical Net Burn & Cash Runway Equations
            net_burn = expenses - raw_revenue
            is_profitable = net_burn <= 0

            if is_profitable:
                runway_display = "Infinite (Profitable)"
                runway_status = "green"
            else:
                # Runway = current cash / net monthly burn rate
                runway_months = round(cash / net_burn, 1) if net_burn > 0 else 99
                runway_display = f"{runway_months} Months"
                runway_status = "red" if runway_months <= 6.0 else "green"

            # Calculate predictive 12-month insolvency risk curve variables mathematically
            final_risk = 15.0 if is_profitable else min(100.0, 30.0 + (expenses / max(1.0, raw_revenue)) * 20.0)

            # Feature 2: Execute Anomaly Checks
            detected_anomalies = self.scan_for_anomalies(expenses)

            vitality_index = self.compute_vitality_index(raw_revenue, expenses, cash, growth, final_risk)
            vitality_components = self.compute_vitality_components(raw_revenue, expenses, cash, growth, final_risk)
            trend_labels, trend_values, trend_revenue_series, trend_expense_series = self.project_growth_trend(raw_revenue, expenses, cash, growth, final_risk)
            vitality_direction = "Growth" if trend_values[-1] >= trend_values[0] else "Decline"
            vitality_delta = round(trend_values[-1] - trend_values[0], 1)

            # Phase 4: Supply chain tips & alternative financing eligibility
            supply_chain_optimization = self.generate_supply_chain_tips(raw_revenue, expenses, final_risk)
            alternative_financing = self.generate_alternative_financing(runway_status, vitality_index)

            base_matrix = {
                "username": session.get('username', 'Founder'),
                "raw_revenue": raw_revenue,
                "raw_expenses": expenses,
                "raw_cash_reserves": cash,
                "raw_growth_rate": growth,
                "material_price_hike_applied": material_price_hike,
                "revenue": f"${raw_revenue:,.2f}",
                "expenses": f"${expenses:,.2f}",
                "cash_runway": runway_display,
                "growth_rate": f"{growth:.1f}%",
                "risk_score": f"{final_risk:.0f}%",
                "plan_type": plan_type,
                "vitality_index": vitality_index,
                "vitality_direction": vitality_direction,
                "vitality_delta": vitality_delta,
                "vitality_trend_labels": trend_labels,
                "vitality_trend_values": trend_values,
                "vitality_components": vitality_components,
                "vitality_trend_revenue": trend_revenue_series,
                "vitality_trend_expenses": trend_expense_series,
                "anomalies_detected": detected_anomalies,
                "supply_chain_optimization": supply_chain_optimization,
                "alternative_financing": alternative_financing,
                "status_indicators": {
                    "performance": "green" if is_profitable else "red",
                    "runway": runway_status,
                    "growth": "green" if growth >= 0 else "red",
                    "risk": "red" if final_risk >= 50.0 else "green",
                    "vitality": "green" if vitality_direction == "Growth" else "red"
                }
            }
            base_matrix["playbook_tasks"] = self.generate_year_schedule(plan_type, base_matrix)
            return base_matrix
        except Exception as err:
            logging.error(f"Computation failure: {err}")
            return {"error": "Invalid metrics processing."}

matrix_engine = EnterpriseWarningMatrix()

def generate_ai_code(prompt: str) -> str:
    if not gemini_client:
        return ""

    system_instruction = (
        "You are an expert Python developer code generator. "
        "Return ONLY valid, runnable Python code inside a markdown block. "
        "Do not include any conversational explanations, introductions, or warnings outside the code block."
    )

    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        )
    )

    raw_text = response.text or ""
    code_match = re.search(r"```python(.*?)```", raw_text, re.DOTALL)
    return code_match.group(1).strip() if code_match else raw_text.strip()

def execute_in_sandbox(python_code: str):
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    sandbox_globals = {
        "__builtins__": __builtins__,
        "os": None,
        "sys": None,
    }
    sandbox_locals = {}

    success = True
    try:
        exec(python_code, sandbox_globals, sandbox_locals)
    except Exception as err:
        redirected_output.write(f"Execution Error: {err}")
        success = False
    finally:
        sys.stdout = old_stdout

    return success, redirected_output.getvalue()

def format_chat_reply(reply_text):
    if not reply_text:
        return "• No update available."

    text = re.sub(r"\s+", " ", str(reply_text)).strip()
    if not text:
        return "• No update available."

    lines = [line.strip(" -•\n\r") for line in str(reply_text).splitlines() if line.strip()]
    bullets = []

    if lines:
        for line in lines:
            clean = re.sub(r"^[-•\s]+", "", line).strip()
            if clean:
                bullets.append(clean)
    else:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        bullets = sentences

    bullets = [b if len(b) <= 300 else b[:297].rstrip(" ,;:.") + "..." for b in bullets][:5]

    if not bullets:
        return "• No update available."

    return "<br>".join(f"• {b}" for b in bullets)

def build_summary_facts(matrix_data):
    revenue = matrix_data['raw_revenue']
    expenses = matrix_data['raw_expenses']
    margin = revenue - expenses

    return {
        "revenue": revenue,
        "expenses": expenses,
        "margin": margin,
        "is_profitable": margin >= 0,
        "growth_rate": matrix_data['raw_growth_rate'],
        "risk_score": float(matrix_data['risk_score'].replace('%', '')),
        "runway": matrix_data['cash_runway'],
        "direction": matrix_data['vitality_direction'],
        "delta": matrix_data['vitality_delta'],
    }

def generate_rule_based_summary(facts):
    """Builds a short executive narrative strictly from computed facts — no invented numbers."""
    sentences = []

    if facts['growth_rate'] > 0:
        growth_clause = f"Revenue is projected to grow at {facts['growth_rate']:.1f}% per month"
    elif facts['growth_rate'] < 0:
        growth_clause = f"Revenue is projected to decline at {abs(facts['growth_rate']):.1f}% per month"
    else:
        growth_clause = "Revenue is projected to stay flat"

    if facts['is_profitable']:
        expense_clause = f"while expenses remain covered by a ${facts['margin']:,.0f} monthly margin"
    else:
        expense_clause = f"while expenses are outpacing revenue by ${abs(facts['margin']):,.0f} per month"

    sentences.append(f"{growth_clause}, {expense_clause}.")

    if str(facts['runway']).startswith('Infinite'):
        sentences.append(f"Cash reserves are stable with the business currently profitable, and the risk index sits at {facts['risk_score']:.0f}%.")
    else:
        sentences.append(f"At this pace, cash reserves may become strained within {facts['runway']}, with a risk index of {facts['risk_score']:.0f}%.")

    if not facts['is_profitable'] and facts['risk_score'] >= 50:
        sentences.append("Consider reducing discretionary expenses or increasing customer acquisition to protect runway.")
    elif not facts['is_profitable']:
        sentences.append("Consider tightening spend or accelerating revenue to close the gap before it compounds.")
    elif facts['direction'] == 'Decline':
        sentences.append("Consider reviewing growth investments to keep the vitality trend from slipping further.")
    else:
        sentences.append("Current trajectory looks healthy — maintain course and keep monitoring the leading indicators.")

    return " ".join(sentences)

def generate_ai_summary(matrix_data):
    facts = build_summary_facts(matrix_data)
    base_summary = generate_rule_based_summary(facts)

    if not gemini_client:
        return base_summary

    prompt = (
        "Rewrite the following business summary as a tight, natural 2-4 sentence executive brief. "
        "Keep it factually identical — do not invent any numbers, trends, or timeframes that are not "
        f"already present.\n\nSummary: {base_summary}"
    )
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a concise financial analyst. Preserve all facts and numbers exactly; only improve phrasing and flow.",
                temperature=0.2,
            )
        )
        polished = (response.text or "").strip()
        return polished if polished else base_summary
    except Exception as err:
        logging.error(f"AI summary generation failed: {err}")
        return base_summary

def get_cached_ai_summary(matrix_data):
    inputs_key = f"{matrix_data['raw_revenue']}|{matrix_data['raw_expenses']}|{matrix_data['raw_cash_reserves']}|{matrix_data['raw_growth_rate']}"
    inputs_hash = hashlib.md5(inputs_key.encode()).hexdigest()

    cached = session.get('ai_summary_cache')
    if cached and cached.get('hash') == inputs_hash:
        return cached['summary']

    summary = generate_ai_summary(matrix_data)
    session['ai_summary_cache'] = {'hash': inputs_hash, 'summary': summary}
    return summary

def build_session_matrix():
    payload = session.get('matrix_inputs')
    if not payload:
        return None
    matrix_data = matrix_engine.compute_matrix(payload)
    overrides = session.get('task_overrides', {})
    for task in matrix_data.get('playbook_tasks', []):
        if task['id'] in overrides:
            task['status'] = overrides[task['id']]
    return matrix_data

# --- ROUTING WORKFLOW WORKSPACE ---

@app.route('/')
def landing():
    return render_template('lands.html')

@app.route('/features')
def landing_features():
    return render_template('features.html')

@app.route('/how-its-built')
def landing_built():
    return render_template('built.html')

@app.route('/the-model')
def landing_model():
    return render_template('model.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('setup_telemetry'))
    return render_template('login.html', error=None)

@app.route('/setup', methods=['GET', 'POST'])
def setup_telemetry():
    if request.method == 'POST':
        username = request.form.get('user_name', '').strip() or 'Agent'
        session['username'] = username
        
        payload = {
            'revenue': 19500,
            'expenses': 22000,
            'cash_reserves': 45000,
            'growth_rate': 4.5,
            'plan_type': 'daily',
            'material_price_hike': 0  # Initialize sandbox variables safely
        }

        session['matrix_inputs'] = payload
        session['task_overrides'] = {}

        return redirect(url_for('dashboard'))

    return render_template('setup.html')

@app.route('/dashboard')
def dashboard():
    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))
    ai_summary = get_cached_ai_summary(matrix_data)
    return render_template('index.html', matrix=matrix_data, current_view='dashboard', ai_summary=ai_summary)

@app.route('/operational-inputs', methods=['GET', 'POST'])
def operational_inputs():
    if request.method == 'POST':
        payload = {
            'revenue': request.form.get('revenue', type=float) or 0,
            'expenses': request.form.get('expenses', type=float) or 0,
            'cash_reserves': request.form.get('cash_reserves', type=float) or 0,
            'growth_rate': request.form.get('growth_rate', type=float) or 0,
            'plan_type': request.form.get('plan_type', 'daily'),
            'material_price_hike': session.get('matrix_inputs', {}).get('material_price_hike', 0)
        }
        session['matrix_inputs'] = payload
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
        session['task_overrides'] = {}
        return redirect(url_for('operational_inputs'))

    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))

    ai_optimization_suggestions = {
        "suggested_revenue_target": f"${matrix_data['raw_revenue'] * 1.15:,.2f}",
        "suggested_expense_ceiling": f"${matrix_data['raw_expenses'] * 0.90:,.2f}",
        "efficiency_index": "88%",
        "confidence_score": "High"
    }
    return render_template('index.html',
                           matrix=matrix_data,
                           current_view='operational_inputs',
                           ai_suggestions=ai_optimization_suggestions)

@app.route('/sandbox', methods=['GET', 'POST'])
def sandbox():
    """
    Feature 10: Supports real-time interaction sliders processing simulation data.
    """
    if request.method == 'POST':
        # Safely handle post slider recalculation inputs
        current_inputs = session.get('matrix_inputs') or {}
        current_inputs['material_price_hike'] = request.form.get('material_price_hike', type=float) or 0
        session['matrix_inputs'] = current_inputs
        return redirect(url_for('sandbox'))

    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))
    return render_template('index.html', matrix=matrix_data, current_view='sandbox')

@app.route('/complete-playbook')
def complete_playbook():
    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))

    tasks = matrix_data.get('playbook_tasks', [])
    categorized_tasks = {
        "immediate_mitigation": [t for t in tasks if t['category'] == 'Expense Mitigation'],
        "cash_flow_acceleration": [t for t in tasks if t['category'] == 'Invoice Acceleration'],
        "growth_directives": [t for t in tasks if t['category'] == 'Marketing Channels'],
        "automation_scale": [t for t in tasks if t['category'] == 'Digital Automation']
    }
    return render_template('index.html',
                           matrix=matrix_data,
                           current_view='complete_playbook',
                           playbook=categorized_tasks)

@app.route('/risk-analytics')
def risk_analytics():
    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))

    risk_percentage = float(matrix_data['risk_score'].replace('%', ''))

    ai_risk_assessment = {
        "primary_threat_vector": "Burn rate exceeding standard margins" if risk_percentage > 50 else "Stable Operating Velocity",
        "system_vulnerability_rating": "CRITICAL" if risk_percentage > 70 else ("ELEVATED" if risk_percentage > 40 else "MINIMAL"),
        "automated_defense_protocol": "Trigger Expense Lock down Routine" if risk_percentage > 50 else "Maintain Business-As-Usual Allocations"
    }
    return render_template('index.html',
                           matrix=matrix_data,
                           current_view='risk_analytics',
                           risk_analysis=ai_risk_assessment)

@app.route('/node-settings')
def node_settings():
    matrix_data = build_session_matrix()
    if not matrix_data:
        return redirect(url_for('setup_telemetry'))

    node_config = {
        "node_status": "ONLINE",
        "ai_engine_model": "gemini-2.5-flash",
        "telemetry_sync_interval": "Real-time (Stream)",
        "security_clearance": "System Administrator"
    }
    return render_template('index.html',
                           matrix=matrix_data,
                           current_view='node_settings',
                           node_info=node_config)

@app.route('/api/v1/telemetry/recalculate', methods=['POST'])
def recalculate_live():
    payload = request.get_json() or {}
    session['matrix_inputs'] = payload
    session['task_overrides'] = {}
    matrix_output = matrix_engine.compute_matrix(payload)
    return jsonify(matrix_output), 200

@app.route('/api/v1/tasks/toggle', methods=['POST'])
def toggle_task_status():
    payload = request.get_json() or {}
    task_id = payload.get('task_id')
    matrix_data = build_session_matrix()
    if not matrix_data or not task_id: return jsonify({"error": "Missing parameters"}), 400

    for task in matrix_data.get('playbook_tasks', []):
        if task['id'] == task_id:
            new_status = "Completed" if task['status'] != "Completed" else "Pending"
            overrides = session.get('task_overrides', {})
            overrides[task_id] = new_status
            session['task_overrides'] = overrides
            return jsonify({"success": True, "new_status": new_status}), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/api/v1/sandbox/run', methods=['POST'])
def sandbox_run():
    payload = request.get_json() or {}
    prompt = (payload.get('prompt') or '').strip()
    if not prompt:
        return jsonify({"error": "Missing 'prompt'."}), 400
    if not gemini_client:
        return jsonify({"error": "AI engine not configured."}), 503

    try:
        generated_code = generate_ai_code(prompt)
        if not generated_code:
            return jsonify({"error": "Code generation failed."}), 500

        success, output = execute_in_sandbox(generated_code)
        return jsonify({
            "generated_code": generated_code,
            "output": output,
            "success": success
        }), 200
    except Exception as err:
        logging.error(f"Sandbox execution failure: {err}")
        return jsonify({"error": "Sandbox execution failed."}), 500

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
        return jsonify({"reply": format_chat_reply(response.text or "Acknowledged.")}), 200
    except: return jsonify({"reply": "API link timeout."}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True, allow_unsafe_werkzeug=True)