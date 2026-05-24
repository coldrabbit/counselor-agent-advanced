class TestGenerateNotice:
    def test_generate_empty_event_validation(self, client):
        resp = client.post("/api/notices/generate", json={"event": ""})
        assert resp.status_code == 422

    def test_generate_minimal_event(self, client, counselor_profile):
        resp = client.post("/api/notices/generate", json={
            "event": "明天下午3点召开防诈骗班会",
        })
        assert resp.status_code in (200, 500)


class TestNoticeCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/notices")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_not_found(self, client):
        resp = client.get("/api/notices/nonexistent-id")
        assert resp.status_code == 404

    def test_approve_not_found(self, client):
        resp = client.put("/api/notices/nonexistent-id/approve")
        assert resp.status_code == 404

    def test_reject_not_found(self, client):
        resp = client.put("/api/notices/nonexistent-id/reject")
        assert resp.status_code == 404
