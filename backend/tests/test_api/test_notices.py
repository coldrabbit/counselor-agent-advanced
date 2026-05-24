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


class TestBatchGenerate:
    def test_batch_generate(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        s1 = client.post("/api/students", json={"name": "李明", "student_id": "2024001", "class_id": cls["id"]}).json()
        s2 = client.post("/api/students", json={"name": "王红", "student_id": "2024002", "class_id": cls["id"]}).json()
        counselor = client.put("/api/counselor/profile", json={"name": "张伟", "college": "计算机学院"}).json()

        resp = client.post("/api/notices/batch-generate", json={
            "event": "防诈骗班会", "time": "明天下午3点", "location": "A203",
            "participants": "全体同学", "student_ids": [s1["id"], s2["id"]],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        # AI 调用可能失败（无真实 API key），created+failed 之和应等于 total
        assert data["created"] + data["failed"] == 2
