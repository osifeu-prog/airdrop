from decimal import Decimal

def test_token_price_get_set(client):
    r = client.get("/api/v1/token/price")
    assert r.status_code == 200
    assert "price" in r.json()

    r = client.post("/api/v1/token/price", headers={"X-Admin-Secret": "change-me"}, json={"price": "2.5"})
    assert r.status_code == 200
    assert Decimal(r.json()["price"]) == Decimal("2.5")
