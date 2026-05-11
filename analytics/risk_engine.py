import sys
import os

# --- SYSTEM PATH FIX ---
# This ensures Python can find the database folder from inside the analytics folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --- DATABASE MANAGER IMPORT (From Step 2) ---
from database.db_manager import get_db_connection

# Our core risk scoring rules
RISK_RULES = {
    "SQL Injection Detected": 30,
    "Brute Force Attempt": 20,
    "Malware Beacon": 25,
    "Port Scanning": 10
}

def calculate_risk_scores():
    # NEW: Using the central manager!
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # NEW: Use SQL 'GROUP BY' and 'COUNT' to do the heavy lifting instantly
    # Instead of Python counting 5 million rows, the database gives us the exact summary in milliseconds.
    cursor.execute("""
        SELECT ip_address, alert_type, COUNT(*) as attack_count 
        FROM alerts 
        GROUP BY ip_address, alert_type
    """)
    alerts_summary = cursor.fetchall()
    
    ip_risk_map = {}
    
    # Now Python only loops through the small summary, not every single log
    for row in alerts_summary:
        ip = row['ip_address']
        alert_type = row['alert_type']
        attack_count = row['attack_count']
        
        # Get the score for this attack (default to 5 if not in rules)
        score_multiplier = RISK_RULES.get(alert_type, 5) 
        
        # Multiply the score by the number of times they attacked
        total_score = score_multiplier * attack_count
        
        # Add it to their total score
        if ip in ip_risk_map:
            ip_risk_map[ip] += total_score
        else:
            ip_risk_map[ip] = total_score
            
    conn.close()
    return ip_risk_map

if __name__ == "__main__":
    print("🚀 Running Optimized Risk Engine...")
    risks = calculate_risk_scores()
    
    print("\n--- Current Top Threat IPs ---")
    for ip, score in risks.items():
        print(f"IP: {ip} | Total Risk Score: {score}")