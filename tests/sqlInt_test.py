from fastapi.testclient import TestClient
from sqlIntegration import app, create_tables_in_db

test_client = TestClient(app)
create_tables_in_db()

def test_create_item():
    response = test_client.post("/items/", json={"title": "Wine", "description": "Red wine", "year": 2020, "price": 19.99})
    assert response.status_code == 200
    assert response.json()["title"] == "Wine"
    assert response.json()["description"] == "Red wine"
    assert response.json()["year"] == 2020
    assert response.json()["price"] == 19.99

def test_get_items():
    # Create an item first
    test_client.post("/items/", json={"title": "Beer", "description": "Craft beer", "year": 2021, "price": 9.99})
    
    # Now retrieve items with pagination
    response = test_client.get("/items/", params={"offset": 0, "limit": 10})
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert any(item["title"] == "Beer" for item in items)

def test_update_item():
    # Create an item first
    create_response = test_client.post("/items/", json={"title": "Whiskey", "description": "Aged whiskey", "year": 2019, "price": 49.99})
    item_id = create_response.json()["id"]
    
    # Update the item
    update_response = test_client.put(f"/items/{item_id}", json={"title": "Whiskey", "description": "Aged whiskey", "year": 2019, "price": 39.99})
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 39.99

def test_delete_item():
    # Create an item first
    create_response = test_client.post("/items/", json={"title": "Vodka", "description": "Smooth vodka", "year": 2020, "price": 29.99})
    item_id = create_response.json()["id"]

    # Delete the item
    delete_response = test_client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200

    # Verify the item is deleted
    get_response = test_client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_read_item_not_found():
    response = test_client.get("/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found!"