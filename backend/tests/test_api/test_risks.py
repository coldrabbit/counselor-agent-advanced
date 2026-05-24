class TestRiskAPI:
    def test_stats_empty(self, client):
        resp = client.get("/api/risks/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_create_and_list(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "李明", "student_id": "2024001", "class_id": cls["id"], "risk_level": "high"
        }).json()
        resp = client.post("/api/risks", json={
            "student_id": student["id"], "risk_level": "high", "reason": "连续旷课3次"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] == "high"
        assert data["status"] == "NEW"

        resp2 = client.get("/api/risks")
        assert len(resp2.json()) == 1

    def test_update_status(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "王红", "student_id": "2024002", "class_id": cls["id"]
        }).json()
        risk = client.post("/api/risks", json={
            "student_id": student["id"], "risk_level": "medium", "reason": "成绩下滑"
        }).json()
        resp = client.put(f"/api/risks/{risk['id']}", json={"status": "REVIEWING"})
        assert resp.json()["status"] == "REVIEWING"

    def test_stats(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        s1 = client.post("/api/students", json={"name": "A", "student_id": "001", "class_id": cls["id"]}).json()
        s2 = client.post("/api/students", json={"name": "B", "student_id": "002", "class_id": cls["id"]}).json()
        client.post("/api/risks", json={"student_id": s1["id"], "risk_level": "high", "reason": "r1"})
        client.post("/api/risks", json={"student_id": s2["id"], "risk_level": "medium", "reason": "r2"})
        resp = client.get("/api/risks/stats")
        data = resp.json()
        assert data["high"] == 1
        assert data["medium"] == 1
        assert data["total"] == 2

    def test_risk_not_found(self, client):
        resp = client.put("/api/risks/nonexistent", json={"status": "REVIEWING"})
        assert resp.status_code == 404
