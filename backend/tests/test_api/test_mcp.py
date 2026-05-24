class TestMCPTools:
    def test_list_tools(self, client):
        resp = client.get("/api/mcp/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        tool_names = [t["name"] for t in data["tools"]]
        assert "lookup_student" in tool_names
        assert "get_risk_overview" in tool_names
        assert "list_classes" in tool_names

    def test_call_lookup(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        client.post("/api/students", json={"name": "李明", "student_id": "2024001", "class_id": cls["id"]})
        resp = client.post("/api/mcp/call", json={"name": "lookup_student", "arguments": {"query": "李明"}})
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "李明" in data["content"][0]["text"]

    def test_call_risk_overview(self, client):
        resp = client.post("/api/mcp/call", json={"name": "get_risk_overview", "arguments": {}})
        assert resp.status_code == 200
        assert "content" in resp.json()

    def test_call_list_classes(self, client):
        resp = client.post("/api/mcp/call", json={"name": "list_classes", "arguments": {}})
        assert resp.status_code == 200
        assert "content" in resp.json()
