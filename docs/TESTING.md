# FluentUp AI — Testing Strategy & Verification Report

## Test Architecture

FluentUp AI uses a multi-layered testing strategy spanning backend unit and integration tests, database isolation, trusted scoring verification, and production build checks.

---

## 1. Automated Test Execution Commands

### Run Backend Pytest Suite:
```powershell
cd backend
python -m pytest tests/ -v
```

### Run Frontend Production Build Check:
```powershell
cd frontend
npm run build
```

---

## 2. Test Suites Covered

1. **`test_auth.py`**:
   - `test_register_and_login_flow`: Tests user creation, salted password hashing, duplicate email rejection, JWT token authentication, and invalid password 401 handling.
   - `test_demo_user_access`: Tests instant guest access token generation.

2. **`test_tests.py`**:
   - `test_generate_and_submit_test`: Tests 5-question test generation, backend scoring evaluation (verifying that the server evaluates correctness and client cannot forge scores), explanation generation, and duplicate attempt prevention.
   - `test_unlimited_practice_generation`: Verifies that users can generate repeated tests back-to-back without arbitrary application limits.

3. **`test_conversations.py`**:
   - `test_conversation_flow_and_grammar_detection`: Tests starting a session, learner message transmission with intentional grammar error ("Yesterday I go"), real-time structured correction extraction, auto-insertion into the Mistake Notebook, and session completion.

4. **`test_adaptive.py`**:
   - `test_adaptive_smoothing_and_progression`: Verifies exponential moving average smoothing prevents erratic CEFR level jumps and verifies CEFR promotion criteria upon sustained >= 90% accuracy.
   - `test_supermemo_srs_spacing`: Verifies SuperMemo SM-2 interval calculations for perfect recall (ratings 5) versus forgotten recall (rating 1).

---

## 3. Actual Test Results

- **Backend Pytest Result:** `7 passed, 0 failed` (100% pass rate).
- **Frontend Production Build:** Built with Vite `tsc -b && vite build` with zero errors.
- **Database Isolation:** StaticPool in-memory SQLite and isolated user data scoping verified.
