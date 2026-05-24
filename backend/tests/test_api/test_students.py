class TestStudentCRUD:
    def test_create_student(self, client):
        cls = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        }).json()
        resp = client.post("/api/students", json={
            "name": "李明", "student_id": "2024001",
            "class_id": cls["id"], "phone": "13800001111", "risk_level": "low"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "李明"
        assert data["risk_level"] == "low"

    def test_list_with_filters(self, client):
        cls = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        }).json()
        client.post("/api/students", json={
            "name": "李明", "student_id": "2024001", "class_id": cls["id"]
        })
        client.post("/api/students", json={
            "name": "王红", "student_id": "2024002", "class_id": cls["id"]
        })

        resp = client.get(f"/api/students?class_id={cls['id']}")
        assert len(resp.json()) == 2

        resp = client.get("/api/students?search=李明")
        assert len(resp.json()) == 1

    def test_update_student(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "测试", "student_id": "0001", "class_id": cls["id"]
        }).json()
        resp = client.put(f"/api/students/{student['id']}", json={"risk_level": "high"})
        assert resp.status_code == 200
        assert resp.json()["risk_level"] == "high"

    def test_delete_student(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "待删除", "student_id": "9999", "class_id": cls["id"]
        }).json()
        resp = client.delete(f"/api/students/{student['id']}")
        assert resp.json() == {"ok": True}

    def test_get_not_found(self, client):
        assert client.get("/api/students/nonexistent").status_code == 404
