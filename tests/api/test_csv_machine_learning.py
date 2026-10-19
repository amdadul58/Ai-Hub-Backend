import io

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_csv_inspect():
    csv_data = (
        "age,income,city,plan,churn\n"
        "22,25000,Dammam,basic,yes\n"
        "35,50000,Riyadh,premium,no\n"
        "28,32000,Jubail,basic,yes\n"
        "45,75000,Riyadh,premium,no\n"
        "31,42000,Dammam,standard,no\n"
        "24,28000,Jubail,basic,yes\n"
        "52,90000,Riyadh,premium,no\n"
        "29,35000,Dammam,standard,yes\n"
        "41,68000,Jubail,premium,no\n"
        "26,30000,Riyadh,basic,yes\n"
        "38,55000,Dammam,standard,no\n"
        "33,47000,Jubail,basic,no\n"
    ).encode()

    response = client.post(
        "/api/v1/machine-learning/csv/inspect",
        files={"file": ("test.csv", io.BytesIO(csv_data), "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 12
    assert body["column_count"] == 5
    assert "city" in [column["name"] for column in body["columns"]]


def test_csv_train_and_predict(tmp_path, monkeypatch):
    import src.api.v1.csv_machine_learning as csv_ml

    monkeypatch.setattr(csv_ml, "MODEL_DIR", tmp_path)

    rows = [
        (22, 25000, "Dammam", "basic", "yes"),
        (35, 50000, "Riyadh", "premium", "no"),
        (28, 32000, "Jubail", "basic", "yes"),
        (45, 75000, "Riyadh", "premium", "no"),
        (31, 42000, "Dammam", "standard", "no"),
        (24, 28000, "Jubail", "basic", "yes"),
        (52, 90000, "Riyadh", "premium", "no"),
        (29, 35000, "Dammam", "standard", "yes"),
        (41, 68000, "Jubail", "premium", "no"),
        (26, 30000, "Riyadh", "basic", "yes"),
        (38, 55000, "Dammam", "standard", "no"),
        (33, 47000, "Jubail", "basic", "no"),
        (23, 27000, "Riyadh", "basic", "yes"),
        (48, 82000, "Dammam", "premium", "no"),
        (36, 52000, "Jubail", "standard", "no"),
        (27, 31000, "Dammam", "basic", "yes"),
        (55, 95000, "Riyadh", "premium", "no"),
        (32, 44000, "Jubail", "standard", "no"),
        (25, 29000, "Dammam", "basic", "yes"),
        (43, 72000, "Riyadh", "premium", "no"),
    ]

    csv_text = "age,income,city,plan,churn\n" + "".join(
        f"{age},{income},{city},{plan},{churn}\n"
        for age, income, city, plan, churn in rows
    )
    csv_bytes = csv_text.encode()

    train_response = client.post(
        "/api/v1/machine-learning/csv/train",
        data={
            "target_column": "churn",
            "task": "classification",
            "algorithm": "random_forest",
            "model_name": "automated_test.joblib",
            "test_size": "0.2",
        },
        files={"file": ("train.csv", io.BytesIO(csv_bytes), "text/csv")},
    )

    assert train_response.status_code == 200, train_response.text
    assert train_response.json()["status"] == "trained"
    assert (tmp_path / "automated_test.joblib").is_file()

    predict_csv = (
        "age,income,city,plan\n"
        "30,40000,Dammam,standard\n"
        "50,85000,Riyadh,premium\n"
    ).encode()

    predict_response = client.post(
        "/api/v1/machine-learning/csv/predict",
        data={"model_name": "automated_test.joblib"},
        files={"file": ("predict.csv", io.BytesIO(predict_csv), "text/csv")},
    )

    assert predict_response.status_code == 200, predict_response.text
    result = predict_response.json()
    assert result["row_count"] == 2
    assert len(result["predictions"]) == 2


def test_csv_train_rejects_invalid_task():
    response = client.post(
        "/api/v1/machine-learning/csv/train",
        data={
            "target_column": "churn",
            "task": "invalid",
            "algorithm": "random_forest",
            "model_name": "invalid_test.joblib",
            "test_size": "0.2",
        },
        files={
            "file": (
                "test.csv",
                io.BytesIO(b"a,b\n1,yes\n2,no\n"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
