from app.db.seed_monthly_tasks import MONTHLY_TASK_SEEDS, seed_monthly_tasks
from app.models.monthly_task import MonthlyTask


def test_get_monthly_tasks_success(client):
    resp = client.get("/api/monthly-tasks?month=5")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 8
    assert {item["month"] for item in data} == {5}
    assert data == sorted(data, key=lambda item: (item["category"], item["title"]))
    assert {
        "id",
        "month",
        "category",
        "title",
        "description",
        "action_type",
        "action_label",
        "action_params",
    }.issubset(data[0].keys())


def test_get_monthly_tasks_invalid_month_negative(client):
    resp = client.get("/api/monthly-tasks?month=0")

    assert resp.status_code == 422


def test_get_monthly_tasks_invalid_month_exceed(client):
    resp = client.get("/api/monthly-tasks?month=13")

    assert resp.status_code == 422


def test_get_monthly_tasks_missing_param(client):
    resp = client.get("/api/monthly-tasks")

    assert resp.status_code == 422


def test_seed_data_covers_twelve_months_and_required_fields():
    months = {item["month"] for item in MONTHLY_TASK_SEEDS}
    categories_by_month = {
        month: {item["category"] for item in MONTHLY_TASK_SEEDS if item["month"] == month}
        for month in range(1, 13)
    }

    assert months == set(range(1, 13))
    assert all(len(categories) == 8 for categories in categories_by_month.values())
    for item in MONTHLY_TASK_SEEDS:
        assert item["id"]
        assert 1 <= item["month"] <= 12
        assert item["category"]
        assert item["title"]
        assert item["description"]
        assert item["action_type"] in {"notice", "talk", "todo"}
        assert item["action_label"]
        assert isinstance(item["action_params"], dict)


def test_seed_idempotent(db_session):
    seed_monthly_tasks(db_session)
    first_count = db_session.query(MonthlyTask).count()

    seed_monthly_tasks(db_session)
    second_count = db_session.query(MonthlyTask).count()

    assert first_count == len(MONTHLY_TASK_SEEDS)
    assert second_count == first_count
