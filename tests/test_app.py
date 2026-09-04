from fastapi.testclient import TestClient

from todo_api.app import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_todo():
    response = client.post("/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["done"] is True
    assert "id" in data


def test_list_todos():
    client.post("/todos", json={"title": "Walk the dog"})
    response = client.get("/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_todo_not_found():
    response = client.get("/todos/9999")
    assert response.status_code == 404


def test_update_todo():
    create_resp = client.post("/todos", json={"title": "Original"})
    todo_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/todos/{todo_id}", json={"title": "Updated", "done": True}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated"
    assert update_resp.json()["done"] is True


def test_delete_todo():
    create_resp = client.post("/todos", json={"title": "Temporary"})
    todo_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/todos/{todo_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/todos/{todo_id}")
    assert get_resp.status_code == 404
