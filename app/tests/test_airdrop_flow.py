from decimal import Decimal

def test_airdrop_request_and_approve(client):
    # create user
    telegram_id = 111
    r = client.get("/api/v1/user/info", params={"telegram_id": telegram_id})
    assert r.status_code == 200

    # request airdrop
    r = client.post("/api/v1/airdrop/request", params={"telegram_id": telegram_id}, json={"amount": "10"})
    assert r.status_code == 200, r.text
    airdrop_id = r.json()["id"]
    assert r.json()["status"] == "pending"

    # approve (admin secret)
    r = client.post("/api/v1/airdrop/approve", headers={"X-Admin-Secret": "change-me"}, json={"airdrop_id": airdrop_id})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"

    # wallet increased
    r = client.get("/api/v1/wallet/balance", params={"telegram_id": telegram_id})
    assert r.status_code == 200
    assert Decimal(r.json()["balance"]) == Decimal("10")
