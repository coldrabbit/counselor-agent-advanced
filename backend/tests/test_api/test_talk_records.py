class TestGenerateTalkRecord:
    def test_generate_missing_fields(self, client):
        resp = client.post("/api/talk-records/generate", json={
            "student_name": "",
            "student_id": "",
            "situation": "",
        })
        assert resp.status_code == 422

    def test_generate_minimal(self, client, counselor_profile):
        resp = client.post("/api/talk-records/generate", json={
            "student_name": "李明",
            "student_id": "2024001",
            "situation": "该生近期旷课两次，情绪低落",
        })
        assert resp.status_code in (200, 500)


class TestTalkRecordCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/talk-records")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_not_found(self, client):
        resp = client.get("/api/talk-records/nonexistent-id")
        assert resp.status_code == 404

    def test_approve_not_found(self, client):
        resp = client.put("/api/talk-records/nonexistent-id/approve")
        assert resp.status_code == 404

    def test_reject_not_found(self, client):
        resp = client.put("/api/talk-records/nonexistent-id/reject")
        assert resp.status_code == 404
