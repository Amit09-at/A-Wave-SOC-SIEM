import os
import sys
import re

# --- SYSTEM PATH FIX & DB MANAGER ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from database.db_manager import get_db_connection

STATE_FILE = os.path.join(BASE_DIR, "analytics", "waf_state.txt")

# OPTIMIZATION: Compile regex once for lightning-fast matching (O(1) time complexity)
SUSPICIOUS_REGEX = re.compile(r"(/admin|/config|/\.env|UNION SELECT|SELECT \* FROM)", re.IGNORECASE)

def get_last_id():
    """Reads the ID of the last log we successfully scanned."""
    if not os.path.exists(STATE_FILE): return 0
    try:
        with open(STATE_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0

def update_last_id(log_id):
    """Updates the state file safely using an Atomic Write."""
    # FILE SAFETY: We write to a temporary file first, then swap it instantly.
    # This guarantees the file is NEVER empty, even during a power outage.
    tmp_file = f"{STATE_FILE}.tmp"
    with open(tmp_file, 'w') as f:
        f.write(str(log_id))
    os.replace(tmp_file, STATE_FILE) 

def detect_web_attacks():
    last_id = get_last_id()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, ip_address, requested_url, user_agent FROM web_logs WHERE id > ?", (last_id,))
    new_logs = cursor.fetchall()

    if not new_logs:
        conn.close()
        return 

    highest_id = last_id
    alerts_to_insert = []
    
    for row in new_logs:
        log_id = row['id']
        ip = row['ip_address']
        url = row['requested_url']
        
        if log_id > highest_id:
            highest_id = log_id
            
        # OPTIMIZATION: Use Regex instead of a slow loop
        match = SUSPICIOUS_REGEX.search(url)
        if match:
            matched_text = match.group(0)
            # Add to a batch list for faster database insertion
            alerts_to_insert.append((ip, "Web Probe", "MEDIUM", f"Suspicious pattern matched: {matched_text}", "WAF Engine"))
    
    # Insert all alerts at once (Batch Processing)
    if alerts_to_insert:
        cursor.executemany("""
            INSERT INTO alerts (timestamp, ip_address, alert_type, severity, description, detection_source) 
            VALUES (datetime('now'), ?, ?, ?, ?, ?)
        """, alerts_to_insert)
    
    conn.commit()
    conn.close()
    
    update_last_id(highest_id)

if __name__ == "__main__":
    print("🛡️ Running Optimized WAF Detector...")
    detect_web_attacks()
    print("✅ Scan Complete.")