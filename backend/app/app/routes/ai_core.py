import os
import re
from flask import Blueprint, request, jsonify, session
from google import genai
from google.genai import types

ai_bp = Blueprint('ai_core', __name__)


def format_chat_reply(reply_text):
    """Format AI reply into up to 5 readable bullet points.

    Keeps full sentences (larger length) and preserves line breaks using HTML <br>.
    """
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

# Wake up the official Google Gemini SDK Engine client
api_key = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key) if api_key else None

@ai_bp.route('/api/v1/chat', methods=['POST'])
def chat_gateway():
    """Core Endpoint managing interactive Gemini co-pilot intelligence queries."""
    if not gemini_client:
        return jsonify({"reply": format_chat_reply("[EMULATION MODE] Add your GEMINI_API_KEY to enable live AI answers.")}), 200

    payload = request.get_json() or {}
    user_msg = payload.get('message', '')
    current_matrix = payload.get('current_matrix', {})

    # Frame the behavioral persona and insert current metrics direct context parameters
    system_instruction = f"""
    You are the advanced Gemini Neo-Core Engine (v2.5-flash), the master AI financial brain of this command deck.
    
    Active Telemetry:
    - Monthly Inflow Balance: {current_matrix.get('revenue', '$0.00')}
    - Expense Burn Outflow: {current_matrix.get('expenses', '$0.00')}
    - Computed Timeline Runway: {current_matrix.get('cash_runway', 'Unknown')}
    - Risk Matrix Threshold: {current_matrix.get('risk_score', '0%')}
    
    Your technical directives cover managing 12 platform capabilities: highlighting anomalous habits, explaining statistical metrics clearly, framing operational cost-cutting strategies, and outputting actionable marketing email templates on demand to generate cash. 
    
    Respond in 3 bullet points max. Keep each bullet short, practical, and easy to scan. Avoid long paragraphs.
    """

    try:
        # Trigger real-time completion using the 2026 google-genai specifications
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_msg,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=800
            )
        )
        reply_text = response.text or "No update available."
        return jsonify({"reply": format_chat_reply(reply_text)}), 200

    except Exception as err:
        return jsonify({"reply": f"Gemini pipeline latency timeout. Vector trace: {str(err)}"}), 500