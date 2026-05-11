import sys
import os
from unittest.mock import patch, MagicMock

# Allow the test file to see our main project folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from analytics.risk_engine import RISK_RULES, calculate_risk_scores

def test_risk_rules_exist():
    """
    Test 1: Ensure critical security rules are not accidentally deleted or changed.
    """
    assert "SQL Injection Detected" in RISK_RULES
    assert RISK_RULES["SQL Injection Detected"] == 30
    assert "Brute Force Attempt" in RISK_RULES

# --- 🚀 SENIOR UPGRADE: DATABASE MOCKING ---
@patch('analytics.risk_engine.get_db_connection')
def test_risk_math_logic(mock_get_db):
    """
    Test 2: Ensure the math is exactly correct WITHOUT connecting to the real database.
    """
    # 1. Trick Python into thinking it connected to the DB
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # 2. Feed it Fake Database Rows (3 SQL Injections, 1 Brute Force)
    mock_cursor.fetchall.return_value = [
        {'ip_address': '10.0.0.1', 'alert_type': 'SQL Injection Detected', 'attack_count': 3},
        {'ip_address': '10.0.0.2', 'alert_type': 'Brute Force Attempt', 'attack_count': 1}
    ]
    
    # 3. Run the Risk Engine on our Fake Data
    results = calculate_risk_scores()
    
    # 4. ASSERT THE MATH IS CORRECT!
    # SQLi Score = 30. We had 3 attacks. 30 * 3 = 90.
    assert results['10.0.0.1'] == 90
    
    # Brute Force Score = 20. We had 1 attack. 20 * 1 = 20.
    assert results['10.0.0.2'] == 20

    print("\n✅ MATH TEST PASSED: 30 * 3 = 90")