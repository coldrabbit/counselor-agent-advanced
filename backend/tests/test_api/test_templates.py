class TestTemplateCRUD:
    def test_create_and_list(self, client):
        resp = client.post("/api/templates", json={
            "name": "防诈骗班会通知", "category": "安全", "content": "明天下午3点召开防诈骗班会，地点A203"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "防诈骗班会通知"
        assert data["category"] == "安全"

        resp2 = client.get("/api/templates")
        assert len(resp2.json()) == 1

    def test_filter_by_category(self, client):
        client.post("/api/templates", json={"name": "A", "category": "安全", "content": "test"})
        client.post("/api/templates", json={"name": "B", "category": "学风", "content": "test"})
        resp = client.get("/api/templates?category=安全")
        assert len(resp.json()) == 1

    def test_update(self, client):
        tmpl = client.post("/api/templates", json={"name": "旧名", "category": "通用", "content": "旧内容"}).json()
        resp = client.put(f"/api/templates/{tmpl['id']}", json={"name": "新名"})
        assert resp.json()["name"] == "新名"

    def test_delete(self, client):
        tmpl = client.post("/api/templates", json={"name": "待删", "category": "通用", "content": "test"}).json()
        resp = client.delete(f"/api/templates/{tmpl['id']}")
        assert resp.json() == {"ok": True}

    def test_not_found(self, client):
        assert client.put("/api/templates/nonexistent", json={"name": "x"}).status_code == 404
        assert client.delete("/api/templates/nonexistent").status_code == 404
