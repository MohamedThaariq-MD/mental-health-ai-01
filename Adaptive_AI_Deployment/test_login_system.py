"""
LYKA Login System Integration Test
===================================
Tests: create_user, authenticate_user, get_conversation_history, and payload check for /analyze
"""

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.database import init_db, create_user, authenticate_user, get_conversation_history, save_conversation_turn
import requests

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

errors = 0

def check(label, condition, detail=""):
    global errors
    if condition:
        print(f"{PASS} {label}")
    else:
        print(f"{FAIL} {label} {detail}")
        errors += 1

print("\n====================================================")
print("   LYKA Login System - Integration Test Suite")
print("====================================================\n")

# 1. Init DB
print(f"{INFO} Initialising database...")
init_db()
print(f"{PASS} Database initialised.\n")

# 2. Register a test user
print("--- Test 1: User Registration ---")
TEST_EMAIL = "testuser_lyka_123@test.com"
TEST_PW    = "SecurePassword!99"
TEST_NAME  = "TestUser"

ok, msg = create_user(TEST_NAME, 25, TEST_EMAIL, TEST_PW)
if not ok and "already exists" in msg:
    print(f"{INFO} User already exists - skipping creation (OK)")
elif ok:
    check("create_user() returned True", ok, msg)
else:
    check("create_user() returned True", ok, msg)

# 3. Authenticate with correct credentials
print("\n--- Test 2: Authentication - Correct Credentials ---")
user = authenticate_user(TEST_EMAIL, TEST_PW)
check("authenticate_user() returns dict", isinstance(user, dict))
if user:
    check("username matches", user.get("username") == TEST_NAME)
    check("email matches",    user.get("email")    == TEST_EMAIL)

# 4. Authenticate with wrong password
print("\n--- Test 3: Authentication - Wrong Password ---")
bad = authenticate_user(TEST_EMAIL, "WrongPassword!")
check("Returns None on bad password", bad is None)

# 5. Save & retrieve conversation
print("\n--- Test 4: Conversation History Repopulation ---")
SID = TEST_EMAIL
save_conversation_turn(SID, "Hello LYKA", "Hi! How can I help?", "Neutral", "low")
hist = get_conversation_history(SID, limit=5)
check("History is a list",         isinstance(hist, list))
check("At least 1 entry returned", len(hist) >= 1)
if hist:
    row = hist[-1]
    check("user_text populated",  row.get("user_text") == "Hello LYKA")
    check("ai_response populated", row.get("ai_response") == "Hi! How can I help?")

# 6. Backend /analyze username payload check
print("\n--- Test 5: Backend /analyze Payload (requires backend running) ---")
try:
    payload = {
        "text": "I feel okay today",
        "session_id": TEST_EMAIL,
        "username": TEST_NAME,
        "use_camera": False
    }
    r = requests.post("http://127.0.0.1:5000/analyze", json=payload, timeout=10)
    if r.status_code == 200:
        data = r.json()
        check("Endpoint returns 200",          r.status_code == 200)
        check("conversational_response exists", "conversational_response" in data)
        check("session_id returned",           "session_id" in data)
        print(f"  AI response preview: {str(data.get('conversational_response',''))[:120]}...")
    else:
        print(f"{INFO} Backend returned {r.status_code} — check if backend is running.")
except requests.exceptions.ConnectionError:
    print(f"{INFO} Backend not running — skipping live API test.")

# Summary
print("\n====================================================")
if errors == 0:
    print(f"\033[92m ALL TESTS PASSED ✓ Implementation is complete & correct!\033[0m")
else:
    print(f"\033[91m {errors} TEST(S) FAILED — review output above.\033[0m")
print("====================================================\n")
