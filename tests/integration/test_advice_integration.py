import requests

def test_advice_endpoint():
    response = requests.post(
        "http://backend:8000/api/advice",
        json={"text": "Tell me some advice"}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["advice"] == "This is a mock advice for integration testing."
