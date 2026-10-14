def get_auth_headers(client):
    res = client.post("/api/v1/auth/demo")
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_generate_and_submit_test(client):
    headers = get_auth_headers(client)

    # 1. Generate 5-question test
    gen_res = client.post(
        "/api/v1/tests/generate",
        json={"topic": "tenses", "cefr_level": "A2", "question_count": 5, "test_mode": "quick_5"},
        headers=headers,
    )
    assert gen_res.status_code == 200, gen_res.text
    gen_data = gen_res.json()
    assert "attempt_id" in gen_data
    assert len(gen_data["questions"]) == 5
    attempt_id = gen_data["attempt_id"]

    # 2. Submit answers
    answers = []
    for q in gen_data["questions"]:
        # Select first option for testing
        answers.append({
            "question_id": q["id"],
            "user_answer": q["options"][0],
        })

    sub_res = client.post(
        f"/api/v1/tests/{attempt_id}/submit",
        json={"time_taken_seconds": 45, "answers": answers},
        headers=headers,
    )
    assert sub_res.status_code == 200, sub_res.text
    sub_data = sub_res.json()
    assert "score_percentage" in sub_data
    assert "correct_count" in sub_data
    assert "results" in sub_data
    assert len(sub_data["results"]) == 5

    # 3. Test duplicate submission protection
    dup_sub = client.post(
        f"/api/v1/tests/{attempt_id}/submit",
        json={"time_taken_seconds": 45, "answers": answers},
        headers=headers,
    )
    assert dup_sub.status_code == 400

    # 4. Check test history
    hist_res = client.get("/api/v1/tests/history", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1


def test_unlimited_practice_generation(client):
    """Verifies user can generate multiple tests back to back without artificial caps."""
    headers = get_auth_headers(client)

    for i in range(3):
        res = client.post(
            "/api/v1/tests/generate",
            json={"topic": "articles", "cefr_level": "B1", "question_count": 5, "test_mode": "quick_5"},
            headers=headers,
        )
        assert res.status_code == 200
        assert "attempt_id" in res.json()
