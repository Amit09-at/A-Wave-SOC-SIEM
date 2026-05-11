import time
import random
from datetime import datetime
import os
import sys

# --- SYSTEM PATH FIX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from database.db_manager import get_db_connection
from analytics.threat_intel import get_ip_intelligence

# --- ADVANCED ATTACK SCENARIOS ---
# Format: (List_of_IPs, Alert_Type, Severity, Description_Template)
ATTACK_SCENARIOS = [
    # 1. Web Application Attacks (WAF Triggers)
    (["185.70.41.130", "46.17.40.100", "93.184.216.34"], "SQL Injection", "CRITICAL", "Payload: ' OR 1=1; DROP TABLE users; --"),
    (["114.114.114.114", "223.252.19.130"], "Cross-Site Scripting (XSS)", "HIGH", "Reflected XSS payload detected in /search?q="),
    (["177.10.15.20", "200.15.45.90"], "Local File Inclusion (LFI)", "CRITICAL", "Attempt to access /etc/passwd via path traversal"),
    (["104.18.32.10", "104.20.15.22"], "Remote Code Execution (RCE)", "CRITICAL", "Apache Struts CVE-2017-5638 exploitation attempt"),

    # 2. Authentication & Credential Attacks
    (["8.8.8.8", "8.8.4.4"], "Brute Force Attempt", "HIGH", "100+ failed SSH logins for user 'root' in 2 minutes"),
    (["89.208.29.11", "193.106.120.25"], "Credential Stuffing", "HIGH", "High-frequency login attempts using leaked credential dumps"),
    (["192.168.1.55", "10.0.0.12"], "Password Spraying", "MEDIUM", "Multiple internal accounts targeted with 'Password123!'"),

    # 3. Network & Infrastructure Volumetric Attacks
    (["1.1.1.1", "1.0.0.1"], "DDoS SYN Flood", "CRITICAL", "Inbound traffic spike: 50,000 packets/sec on port 443"),
    (["212.193.116.1", "5.188.86.10"], "Aggressive Port Scan", "MEDIUM", "Nmap SYN stealth scan detected across all 65535 ports"),

    # 4. Malware & Advanced Persistent Threats (APT)
    (["185.220.101.5", "185.220.101.10"], "Ransomware Callback", "CRITICAL", "Outbound connection to known LockBit C2 server"),
    (["91.240.118.22", "195.123.210.10"], "Data Exfiltration", "HIGH", "Unusual outbound transfer of 5GB to unknown external IP"),
    (["192.168.1.105", "10.0.0.99"], "Malware Beacon", "HIGH", "Internal host sending periodic heartbeats to external domain"),

    # 5. Insider Threats & Lateral Movement
    (["192.168.1.200"], "Insider Threat", "MEDIUM", "Large archive (ZIP) creation of sensitive /finance directory"),
    (["10.0.0.45"], "Privilege Escalation", "HIGH", "Standard user attempting 'sudo su' multiple times off-hours")
]

def simulate_enriched_attacks():
    print("🌍 STARTING ADVANCED THREAT SIMULATION...")
    print("   (Generating diverse, realistic attack vectors globally...)")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        while True:
            # 1. Pick a random attack scenario
            ip_pool, alert_type, severity, base_desc = random.choice(ATTACK_SCENARIOS)
            
            # 2. Pick a random IP from the assigned geographical pool
            ip = random.choice(ip_pool)
            
            # 3. OSINT ENRICHMENT STEP
            intel = get_ip_intelligence(ip)
            
            # 4. Format description with intelligence
            enriched_desc = f"{base_desc} [{intel['flag']} {intel['country']} | ISP: {intel['isp']}]"
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 5. Insert into Database
            cursor.execute("""
                INSERT INTO alerts (timestamp, ip_address, alert_type, severity, description, detection_source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, ip, alert_type, severity, enriched_desc, "AI-Enriched Engine"))

            conn.commit()
            
            # Console output for dramatic demo effect
            icon = "🔥" if severity == "CRITICAL" else "🚨"
            print(f"{icon} ALERT: {alert_type} from {intel['country']} ({ip})")
            
            # 6. Organic Timing: Fire attacks between 1 and 4 seconds apart
            time.sleep(random.uniform(1.0, 4.0)) 

    except KeyboardInterrupt:
        print("\n🛑 Advanced Simulation Stopped.")
    except Exception as e:
        print(f"⚠️ Simulation Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    simulate_enriched_attacks()