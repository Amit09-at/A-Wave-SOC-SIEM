import time
import logging
import os
import sys
import threading

# --- SYSTEM PATH FIX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# --- ENGINE IMPORTS ---
from analytics.risk_engine import calculate_risk_scores
from analytics.web_attack_detector import detect_web_attacks
from analytics.deception import monitor_honeyfile

# --- LOGGING SETUP ---
logging.basicConfig(
    filename=os.path.join(BASE_DIR, 'logs', 'system.log'),
    level=logging.INFO,
    format='%(asctime)s - [ENGINE] - %(levelname)s - %(message)s'
)

def run_risk_engine():
    """Periodically calculates risk scores based on aggregated alerts."""
    while True:
        try:
            logging.info("Core Engine: Calculating Risk Scores...")
            top_risks = calculate_risk_scores()
            for ip, score in top_risks.items():
                if score >= 50:
                    logging.error(f"CRITICAL RISK: IP {ip} reached score {score}")
            time.sleep(15) 
        except Exception as e:
            logging.error(f"Error in Risk Engine: {e}")
            time.sleep(5)

def run_waf_engine():
    """Continuously scans NEW web logs for regex-based attack patterns."""
    while True:
        try:
            logging.info("WAF Engine: Scanning incoming web traffic...")
            detect_web_attacks()
            time.sleep(5) # Fast polling for security
        except Exception as e:
            logging.error(f"Error in WAF Engine: {e}")
            time.sleep(5)

def run_deception_engine():
    """Starts the Honeyfile monitor in its own thread."""
    try:
        logging.info("Deception Engine: Arming Honeyfile Traps...")
        monitor_honeyfile() # This has its own internal loop
    except Exception as e:
        logging.error(f"Error in Deception Engine: {e}")

def main():
    print("🌊 A-WAVE SOC ORCHESTRATOR STARTING...")
    print("---------------------------------------")
    print("🛡️  WAF Engine:       [RUNNING]")
    print("📈  Risk Engine:      [RUNNING]")
    print("🪤  Deception Engine: [RUNNING]")
    print("📂  Activity Log:     'logs/system.log'")
    print("---------------------------------------")
    
    # 🧵 MULTITHREADING: Run all engines at once!
    threads = [
        threading.Thread(target=run_waf_engine, daemon=True),
        threading.Thread(target=run_risk_engine, daemon=True),
        threading.Thread(target=run_deception_engine, daemon=True)
    ]

    for t in threads:
        t.start()

    try:
        # Keep the main script alive while threads do the work
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down SOC engines...")
        logging.info("SOC Engines gracefully shut down by administrator.")

if __name__ == "__main__":
    main()