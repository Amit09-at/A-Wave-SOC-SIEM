import os
import sys
import pickle
import pandas as pd
from sklearn.ensemble import IsolationForest

# --- SYSTEM PATH FIX & DB MANAGER ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from database.db_manager import get_db_connection

def train():
    print("🧠 Connecting to database to fetch REAL traffic data...")
    conn = get_db_connection()
    
    # Fetch real logs instead of using np.random!
    query = """
        SELECT 
            LENGTH(requested_url) as url_length,
            http_status
        FROM web_logs
    """
    
    # Pandas can read SQL queries directly into a DataFrame!
    df = pd.read_sql_query(query, conn)
    conn.close()

    if len(df) < 2:
        print("⚠️ Not enough real data to train. Please generate some web logs first.")
        return

    print(f"📊 Training AI Model on {len(df)} real log entries...")
    
    # Train the Isolation Forest strictly on the real features we extracted
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(df[['url_length', 'http_status']])

    # Save the Brain
    models_dir = os.path.join(BASE_DIR, "ai_engine", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "iso_forest.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"✅ REAL Model trained and saved to {model_path}")
    print("   - The AI has now learned the baseline of your ACTUAL network traffic!")

if __name__ == "__main__":
    train()