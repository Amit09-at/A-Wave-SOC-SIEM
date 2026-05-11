import os
import sqlite3
from datetime import datetime
import bcrypt  

# --- CONFIGURATION ---
PROJECT_NAME = "A-Wave"
DB_PATH = os.path.join("database", "awave.db")

# Define the folder structure
FOLDERS = [
    "database",
    "logs",
    "logs/sample_logs",
    "logs/apache",
    "backend",
    "static",
    "static/css",
    "static/js",
    "analytics",
    "parsers",
    "ai_engine",
    "config",
    "tests" # <--- Added tests folder to structure
]

# --- 1. CREATE DIRECTORIES ---
def create_directories():
    print(f"[*] Setting up {PROJECT_NAME} directory structure...")
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
        print(f"   CREATED: {folder}/")

# --- 2. CREATE DATABASE & TABLES ---
def create_database():
    print(f"[*] Initializing Database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 🚀 SENIOR UPGRADE: ENABLE WAL MODE ---
    # This allows simultaneous reading and writing, preventing "Database Locked" crashes!
    cursor.execute('PRAGMA journal_mode=WAL;')
    print("   🚀 ENTERPRISE UPGRADE: SQLite Write-Ahead Logging (WAL) Enabled.")

    # Table: Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    # Table: Auth Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auth_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        log_type TEXT,
        source_system TEXT,
        ip_address TEXT,
        event_type TEXT,
        status TEXT,
        raw_log TEXT
    );
    """)

    # Table: Web Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ip_address TEXT,
        request_method TEXT,
        requested_url TEXT,
        http_status INTEGER,
        user_agent TEXT
    );
    """)

    # Table: Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ip_address TEXT,
        alert_type TEXT,
        severity TEXT,
        description TEXT,
        detection_source TEXT
    );
    """)

    # --- INSERT DEFAULT DATA ---
    
    # 1. Default Users (Admin, Manager, Analyst) SECURED WITH BCRYPT
    users = [
        ('admin', bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'admin'),
        ('manager', bcrypt.hashpw('manager123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'manager'),
        ('analyst', bcrypt.hashpw('analyst123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'analyst')
    ]
    cursor.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", users)
    print("   ADDED: Default Users with SECURE HASHED PASSWORDS")

    # 2. Dummy Alerts
    dummy_alerts = [
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '192.168.1.50', 'Brute Force Attempt', 'HIGH', '50 failed login attempts in 1 min', 'Rule Engine'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '10.0.0.8', 'SQL Injection Detected', 'CRITICAL', "Payload: ' OR 1=1 --", 'WAF Log'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '45.33.22.11', 'Port Scanning', 'MEDIUM', 'Sequential port access (20,21,22,80)', 'Network Sniffer'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '172.16.0.5', 'Malware Beacon', 'HIGH', 'Connection to known C2 server', 'Threat Intel')
    ]
    cursor.executemany("""
        INSERT INTO alerts (timestamp, ip_address, alert_type, severity, description, detection_source) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, dummy_alerts)

    # 3. Dummy Web Logs (For AI Training)
    dummy_logs = [
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '192.168.1.50', 'POST', '/admin/login.php', 401, 'Mozilla/5.0'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '10.0.0.8', 'GET', '/search?q=test', 200, 'Chrome/90.0'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '45.33.22.11', 'GET', '/.env', 403, 'Python-urllib/3.8'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '10.0.0.9', 'GET', '/index.html', 200, 'Mozilla/5.0'),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '10.0.0.10', 'GET', '/about.html', 200, 'Chrome/90.0')
    ]
    cursor.executemany("""
        INSERT INTO web_logs (timestamp, ip_address, request_method, requested_url, http_status, user_agent) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, dummy_logs)
    
    conn.commit()
    conn.close()
    print("   SUCCESS: Database created with sample data.")

# --- 3. CREATE DUMMY LOG FILES ---
def create_dummy_logs():
    print("[*] Generating dummy log files...")
    
    auth_log_path = "logs/sample_logs/auth.log"
    with open(auth_log_path, "w") as f:
        f.write("Feb 10 10:00:00 server sshd[123]: Failed password for root from 192.168.1.10 port 22 ssh2\n")
        f.write("Feb 10 10:00:02 server sshd[123]: Failed password for root from 192.168.1.10 port 22 ssh2\n")
        f.write("Feb 10 10:05:00 server sshd[456]: Accepted password for amit from 10.0.0.5 port 22 ssh2\n")
    
    access_log_path = "logs/apache/access.log"
    with open(access_log_path, "w") as f:
        f.write('192.168.1.10 - - [10/Feb/2026:13:55:36 +0530] "GET /admin.php HTTP/1.1" 404 2326\n')
        f.write('192.168.1.10 - - [10/Feb/2026:13:55:38 +0530] "GET /login.php HTTP/1.1" 200 341\n')
        f.write('45.33.22.11 - - [10/Feb/2026:13:56:00 +0530] "POST /api/v1/upload HTTP/1.1" 500 521\n')
    
    print(f"   CREATED: {auth_log_path}")
    print(f"   CREATED: {access_log_path}")

if __name__ == "__main__":
    create_directories()
    create_database()
    create_dummy_logs()
    print("\n✅ A-WAVE SETUP COMPLETE!")