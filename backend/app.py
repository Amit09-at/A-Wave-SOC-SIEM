import sys
import os
import logging
import requests  
from flask import Flask, jsonify, send_from_directory, request, session, redirect, make_response
import csv
import io
import time
import html
from functools import wraps
from datetime import datetime

# --- SECURITY IMPORTS ---
import bcrypt
from dotenv import load_dotenv

# --- SYSTEM PATH FIX ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --- DATABASE MANAGER IMPORT ---
from database.db_manager import get_db_connection

# --- LOAD SECRETS ---
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, static_folder="../static")
app.secret_key = os.getenv("SECRET_KEY", "fallback_default_key") 

# --- LOGGING SETUP ---
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(BASE_DIR, 'logs', 'system.log'),
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

logging.info("A-Wave Backend Initialized. Server Starting...")

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login.html')
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---
@app.route('/')
def root():
    return redirect('/login.html')

@app.route('/login.html')
def login_page():
    return send_from_directory(app.static_folder, "login.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# --- API: AUTHENTICATION ---
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    db = get_db_connection() 
    user_record = db.execute("SELECT password, role FROM users WHERE username=?", (username,)).fetchone()
    db.close()
    
    if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password'].encode('utf-8')):
        session['user'] = username
        session['role'] = user_record['role']
        logging.info(f"Successful login: User '{username}'")
        return jsonify({"success": True, "role": user_record['role'], "username": username})
        
    logging.warning(f"Failed login attempt: Username '{username}'") 
    return jsonify({"success": False}), 401

@app.route('/api/logout')
def logout():
    user = session.get('user', 'Unknown')
    session.clear()
    logging.info(f"User logged out: '{user}'")
    return jsonify({"success": True})

# --- API: STATS ---
@app.route("/api/stats")
@login_required
def api_stats():
    db = get_db_connection() 
    try:
        total_logs = db.execute("SELECT COUNT(*) FROM web_logs").fetchone()[0]
        total_alerts = db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    except Exception as e: 
        logging.error(f"Database Error in /api/stats: {str(e)}") 
        total_logs = 0; total_alerts = 0
    finally:
        db.close()
    return jsonify({
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "ai_status": "ACTIVE"
    })

# --- API: ALERTS ---
@app.route("/api/alerts")
@login_required
def api_alerts():
    db = get_db_connection() 
    try:
        rows = db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 50").fetchall()
    except Exception as e: 
        logging.error(f"Database Error in /api/alerts: {str(e)}")
        rows = []
    finally:
        db.close()
    return jsonify([dict(row) for row in rows])

# --- API: SCANNER ---
@app.route("/api/scan", methods=['POST'])
@login_required
def run_scan():
    target_ip = request.json.get('ip')
    logging.info(f"Vulnerability scan initiated on '{target_ip}' by user '{session.get('user')}'") 
    time.sleep(1.5) 
    return jsonify({
        "target": target_ip,
        "status": "COMPLETED",
        "ports": [22, 80, 443],
        "risk_score": 85,
        "vulns": ["CVE-2023-023 (SSH)", "Open Port 80"]
    })

# --- API: THREAT INTEL FEED (NEW) ---
@app.route("/api/threat_intel")
@login_required
def get_threat_intel():
    # Mocking a global threat intelligence feed from AlienVault/MITRE
    intel_feed = [
        {"date": datetime.now().strftime('%Y-%m-%d'), "threat": "Ransomware gang 'LockBit' targeting healthcare sectors.", "severity": "CRITICAL"},
        {"date": "2026-05-06", "threat": "New zero-day in Apache Struts (CVE-2026-9912) actively exploited.", "severity": "HIGH"},
        {"date": "2026-05-05", "threat": "Global spike in SSH Brute Force attacks from Botnet-X.", "severity": "MEDIUM"},
        {"date": "2026-05-04", "threat": "Phishing campaign spoofing Microsoft 365 logins.", "severity": "HIGH"}
    ]
    return jsonify({"success": True, "feed": intel_feed})

# --- API: REPORT GENERATOR ---
@app.route('/api/generate_report')
@login_required
def generate_report():
    if request.args.get('type'):
        ip = html.escape(request.args.get('ip', 'Unknown'))
        time_val = html.escape(request.args.get('time', 'Unknown'))
        incident_type = html.escape(request.args.get('type', 'Security Incident'))
        desc = html.escape(request.args.get('desc', 'No description provided.'))
        action = html.escape(request.args.get('action', 'Investigate immediately.'))
        analyst_name = html.escape(session.get('user', 'Analyst').upper())
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        incident_id = hash(time_val) % 10000
        logging.info(f"Incident report generated for IP {ip} by user '{analyst_name}'")

        html_report = f"""
        <html>
        <head>
            <title>A-Wave Security Incident Report</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; padding: 40px; color: #333; }}
                .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #d32f2f; }}
                .title {{ font-size: 18px; font-weight: bold; margin-top: 10px; text-transform: uppercase; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ background: #f4f4f4; padding: 8px; font-weight: bold; border-left: 4px solid #d32f2f; }}
                .content {{ padding: 10px; line-height: 1.6; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 50px; font-size: 12px; text-align: center; color: #777; border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">A-WAVE SOC PLATFORM</div>
                <div class="title">Official Security Incident Report</div>
                <p>Generated by: {analyst_name} | Date: {current_date}</p>
            </div>
            <div class="section">
                <div class="section-title">1. INCIDENT OVERVIEW</div>
                <div class="content">
                    <table>
                        <tr><th>Incident ID</th><td>#{incident_id}</td></tr>
                        <tr><th>Date & Time</th><td>{time_val}</td></tr>
                        <tr><th>Incident Type</th><td>{incident_type}</td></tr>
                        <tr><th>Severity Level</th><td><strong style="color:red">CRITICAL</strong></td></tr>
                    </table>
                </div>
            </div>
            <div class="section">
                <div class="section-title">2. ATTACKER PROFILE</div>
                <div class="content">
                    <strong>Source IP Address:</strong> {ip}<br>
                    <strong>Detection Source:</strong> A-Wave AI Engine<br>
                </div>
            </div>
            <div class="section">
                <div class="section-title">3. TECHNICAL DESCRIPTION</div>
                <div class="content">
                    {desc}
                </div>
            </div>
            <div class="footer">Generated automatically by A-Wave SOC</div>
            <script>window.print();</script> 
        </body>
        </html>
        """
        response = make_response(html_report)
        response.headers["Content-Disposition"] = f"inline; filename=Incident_Report_{ip}.html"
        return response
    
    try:
        db = get_db_connection()
        rows = db.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
        db.close()
        logging.info("CSV Export generated.") 
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(["ID", "Timestamp", "IP", "Type", "Severity", "Description", "Source"])
        cw.writerows(rows)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=soc_report.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        return str(e)

# --- API: LIVE LOG READER ---
@app.route('/api/logs/live')
@login_required
def get_live_logs():
    log_path = os.path.join(BASE_DIR, 'logs', 'system.log')
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()[-30:] # Read the last 30 lines
        return jsonify({"success": True, "logs": "".join(lines)})
    except Exception as e:
        return jsonify({"success": False, "logs": f"Error reading logs: {str(e)}"})

# --- API: AI ASSISTANT BOT ---
@app.route('/api/ai_assist', methods=['POST'])
@login_required
def ai_assist():
    data = request.json
    alert_type = data.get('alert_type', 'Unknown')
    ip = data.get('ip', 'Unknown')

    logging.info(f"User requested AI assistance for threat: {alert_type}")
    
    location_data = "Unknown Location"
    isp_data = "Unknown ISP"
    try:
        if ip != "Unknown":
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
            if response.get("status") == "success":
                location_data = f"{response.get('city')}, {response.get('country')}"
                isp_data = response.get('isp')
    except Exception as e:
        logging.error(f"Internet OSINT lookup failed: {e}")

    time.sleep(1) 

    ai_knowledge = {
        "SQL Injection Detected": {
            "explanation": f"🚨 OSINT DATA: Originated from {location_data} (ISP: {isp_data}). <br><br>The attacker is attempting to inject malicious SQL syntax.",
            "recommendation": "1. Add this IP to your WAF drop-list. \n2. Ensure developers use Parameterized SQL Queries."
        },
        "Brute Force Attempt": {
            "explanation": f"🚨 OSINT DATA: Tracked to {location_data} (ISP: {isp_data}). <br><br>High-frequency credential stuffing attack detected.",
            "recommendation": "1. Implement a 15-minute account lockout. \n2. Enforce MFA across the domain."
        }
    }

    response = ai_knowledge.get(alert_type, {
        "explanation": f"🚨 OSINT DATA: Signal traced to {location_data} (ISP: {isp_data}). <br><br>Analyzed telemetry flagged as '{alert_type}'.",
        "recommendation": "Investigate raw Apache logs and isolate the affected subnet."
    })

    return jsonify({
        "status": "success",
        "ai_analysis": response["explanation"],
        "ai_recommendation": response["recommendation"]
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)