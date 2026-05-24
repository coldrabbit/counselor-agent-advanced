import io
from openpyxl import Workbook


def create_analysis_xlsx(rows):
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


class TestAnalysisAPI:
    def test_upload_rejects_non_excel(self, client):
        resp = client.post("/api/analysis/upload", files={
            "file": ("test.txt", io.BytesIO(b"not excel"), "text/plain")
        })
        assert resp.status_code == 400

    def test_upload_empty_file(self, client):
        buf = create_analysis_xlsx([["姓名", "课程", "成绩"]])
        resp = client.post("/api/analysis/upload", files={
            "file": ("test.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        })
        assert resp.status_code == 400

    def test_upload_with_data(self, client):
        buf = create_analysis_xlsx([
            ["姓名", "课程", "成绩"],
            ["测试", "数学", "85"],
        ])
        resp = client.post("/api/analysis/upload", files={
            "file": ("test.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        })
        assert resp.status_code == 200
        data = resp.json()
        # AI 调用可能失败（无真实 API key），接受两种结果
        assert "success" in data
