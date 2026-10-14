def test_register_and_login_flow(client):
    # 1. Register new user
    reg_payload = {
        "email": "learner@fluentup.ai",
        "password": "SecurePassword123!",
        "display_name": "Rohan Sharma",
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "learner@fluentup.ai"
    assert data["display_name"] == "Rohan Sharma"

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Duplicate registration rejected
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Successful Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "learner@fluentup.ai", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Failed Login on wrong password
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "learner@fluentup.ai", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # 5. Fetch current user
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "learner@fluentup.ai"


def test_demo_user_access(client):
    res = client.post("/api/v1/auth/demo")
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "demo" in data["email"]
