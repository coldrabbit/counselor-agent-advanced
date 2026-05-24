class TestClassCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/classes")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, client):
        resp = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "2024级软件1班"
        assert data["grade"] == "2024"
        assert data["major"] == "软件工程"

        resp2 = client.get("/api/classes")
        assert len(resp2.json()) == 1
