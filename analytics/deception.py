import os
import time
import sys
from datetime import datetime

# --- SYSTEM PATH FIX ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from database.db_manager import get_db_connection

# FIXED: Dynamic absolute path for the trap file
TRAP_FILE = os.path.join(BASE_DIR, "sensitive_data_backup.json")
TRAP_CONTENT = '{"admin_user": "root", "password": "SuperSecretPassword123", "aws_key": "AKIAIOSFODNN7EXAMPLE"}'

def deploy_honeyfile():
    """Creates the bait file."""
    if not os.path.exists(TRAP_FILE):
        with open(TRAP_FILE, "w") as f:
            f.write(TRAP_CONTENT)
        print(f"🪤 HONEYFILE DEPLOYED: {TRAP_FILE}")

def monitor_honeyfile():
    """Watches for ANY file access."""
    deploy_honeyfile()
    last_access_time = os.stat(TRAP_FILE).st_atime
    
    print("🛡️ Deception Engine Active. Watching the trap...")
    
    # FIXED: Using your central, thread-safe db_manager
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        while True:
            try:
                current_access_time = os.stat(TRAP_FILE).st_atime
                
                if current_access_time != last_access_time:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg = f"HONEYTOKEN TRIGGERED! Someone accessed {os.path.basename(TRAP_FILE)}"
                    
                    print(f"🚨 CAUGHT! {msg}")
                    
                    cursor.execute("""
                        INSERT INTO alerts (timestamp, ip_address, alert_type, severity, description, detection_source)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (timestamp, "INTERNAL_HOST", "Honeyfile Trap", "CRITICAL", msg, "Deception Engine"))
                    
                    conn.commit()
                    last_access_time = current_access_time
                    
                time.sleep(2)
            except Exception as e:
                # FIXED: Silent Thread Death prevention. 
                # We log the error, sleep, and CONTINUE instead of breaking the loop.
                print(f"⚠️ Error in Deception Engine: {e}. Retrying in 5s...")
                time.sleep(5)
                continue
                
    except KeyboardInterrupt:
        print("\n🛑 Deception Engine Stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    monitor_honeyfile()