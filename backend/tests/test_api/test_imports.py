import io
from openpyxl import Workbook


def create_test_xlsx(rows):
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


class TestImportStudents:
    def test_import_creates_students(self, client):
        buf = create_test_xlsx([
            ["姓名", "学号", "班级", "手机", "风险等级"],
            ["李明", "2024001", "2024级软件1班", "13800001111", "low"],
            ["王红", "2024002", "2024级软件1班", "13800002222", "medium"],
        ])
        resp = client.post("/api/students/import", files={"file": ("test.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 2
        assert data["skipped"] == 0

    def test_import_auto_creates_class(self, client):
        buf = create_test_xlsx([
            ["姓名", "学号", "班级"],
            ["张三", "2024003", "新班级"],
        ])
        resp = client.post("/api/students/import", files={"file": ("test.xlsx", buf)})
        assert resp.status_code == 200
        classes = client.get("/api/classes").json()
        assert any(c["name"] == "新班级" for c in classes)

    def test_import_rejects_non_excel(self, client):
        resp = client.post("/api/students/import", files={"file": ("test.txt", io.BytesIO(b"not excel"), "text/plain")})
        assert resp.status_code == 400

    def test_import_missing_column(self, client):
        buf = create_test_xlsx([["姓名", "班级"], ["李明", "软件1班"]])
        resp = client.post("/api/students/import", files={"file": ("test.xlsx", buf)})
        assert resp.status_code == 400
