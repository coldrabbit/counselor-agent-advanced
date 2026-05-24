class TestAgentAPI:
    def test_list_agents(self, client):
        resp = client.get("/api/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["agents"]) == 6
        names = [a["name"] for a in data["agents"]]
        assert "notice_agent" in names
        assert "risk_agent" in names
        assert "counseling_agent" in names

    def test_match_notice(self, client):
        resp = client.get("/api/agents/match?description=帮我生成一个通知")
        assert resp.status_code == 200
        assert resp.json()["matched"] == "notice_agent"

    def test_match_risk(self, client):
        resp = client.get("/api/agents/match?description=分析学生风险")
        assert resp.status_code == 200
        assert resp.json()["matched"] == "risk_agent"

    def test_match_fallback(self, client):
        resp = client.get("/api/agents/match?description=不知道要做什么")
        assert resp.status_code == 200
        assert resp.json()["matched"] == "notice_agent"
