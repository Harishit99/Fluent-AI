def get_auth_headers(client):
    res = client.post("/api/v1/auth/demo")
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_conversation_flow_and_grammar_detection(client):
    headers = get_auth_headers(client)

    # 1. Start conversation session
    conv_res = client.post(
        "/api/v1/conversations",
        json={"mode": "instant", "topic": "College & Friends"},
        headers=headers,
    )
    assert conv_res.status_code == 200, conv_res.text
    conv_data = conv_res.json()
    conv_id = conv_data["id"]

    # 2. Learner sends message with intentional grammar mistake: "yesterday I go"
    msg_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": "Yesterday I go to college and meet my friends."},
        headers=headers,
    )
    assert msg_res.status_code == 200, msg_res.text
    msg_data = msg_res.json()
    assert msg_data["sender"] == "assistant"
    assert "content" in msg_data
    assert len(msg_data["content"]) > 0
    # Verify grammar corrections captured
    assert msg_data["corrections"] is not None
    assert len(msg_data["corrections"]) >= 1
    corr = msg_data["corrections"][0]
    assert corr["category"] == "verb_tense"
    assert "went" in corr["corrected"]

    # 3. Check mistake notebook automatically recorded the error
    mistakes_res = client.get("/api/v1/mistakes", headers=headers)
    assert mistakes_res.status_code == 200
    mistakes = mistakes_res.json()
    assert len(mistakes) >= 1
    assert any("go" in m["original_sentence"] for m in mistakes)

    # 4. Finish conversation
    finish_res = client.post(
        f"/api/v1/conversations/{conv_id}/finish",
        json={"summary": "Great practice discussing college routines."},
        headers=headers,
    )
    assert finish_res.status_code == 200
    assert finish_res.json()["status"] == "completed"
