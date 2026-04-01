import json


def test_face_threshold_blocks_below_threshold(app_module, client, register_user, sample_face_image, monkeypatch):
    # Enroll a user with face
    reg = register_user(face_image=sample_face_image)
    assert reg.status_code == 201

    # Force similarity just below threshold (0.80)
    monkeypatch.setattr(app_module.biometric_service, "compare_embeddings", lambda a, b: 0.799)

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123", "face_image": sample_face_image}),
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["success"] is False
    assert "Face verification failed" in data["message"]


def test_face_threshold_allows_at_threshold(app_module, client, register_user, sample_face_image, monkeypatch):
    reg = register_user(face_image=sample_face_image)
    assert reg.status_code == 201

    monkeypatch.setattr(app_module.biometric_service, "compare_embeddings", lambda a, b: 0.80)

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123", "face_image": sample_face_image}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True

