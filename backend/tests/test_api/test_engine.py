class TestEngineAPI:
    def test_run_risk_workflow(self, client):
        resp = client.post("/api/engine/run/risk", json={"risk_level": "high"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("SUCCESS", "WAITING_APPROVAL")
        assert "id" in data

    def test_run_notice_workflow(self, client):
        resp = client.post("/api/engine/run/notice", json={"event": "测试通知"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("SUCCESS", "WAITING_APPROVAL")

    def test_resume_workflow(self, client):
        resp = client.post("/api/engine/run/notice", json={"event": "测试"})
        wf_id = resp.json()["id"]
        resp2 = client.post(f"/api/engine/resume/{wf_id}?action=approve")
        assert resp2.status_code == 200

    def test_unknown_workflow(self, client):
        resp = client.post("/api/engine/run/unknown", json={})
        assert resp.status_code == 400

    def test_status(self, client):
        resp = client.post("/api/engine/run/risk", json={})
        wf_id = resp.json()["id"]
        resp2 = client.get(f"/api/engine/status/{wf_id}")
        assert resp2.status_code == 200
