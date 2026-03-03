import requests
import pytest
import time
import json

import os

FLASK_URL = os.getenv("FLASK_URL", "http://localhost:5000")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

def print_response(title, response):
    print(f"\n--- {title} ---")
    print(f"Status: {response.status_code}")
    try:
        print("Body:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Body: {response.text}")

def test_fastapi_cleanup():
    response = requests.delete(f"{FASTAPI_URL}/api/cleanup")
    print_response("FastAPI Data Cleanup", response)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_flask_health():
    response = requests.get(f"{FLASK_URL}/api/health")
    print_response("Flask Health Check", response)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_flask_customers_pagination():
    # Test page 1, limit 5
    response = requests.get(f"{FLASK_URL}/api/customers?page=1&limit=5")
    print_response("Flask Pagination (Page 1, Limit 5)", response)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["total"] >= 20
    assert data["page"] == 1
    assert data["limit"] == 5

def test_flask_single_customer():
    # Get first customer ID from first page
    resp = requests.get(f"{FLASK_URL}/api/customers?page=1&limit=1")
    customer_id = resp.json()["data"][0]["customer_id"]
    
    response = requests.get(f"{FLASK_URL}/api/customers/{customer_id}")
    print_response(f"Flask Single Customer ({customer_id})", response)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id

def test_fastapi_health():
    response = requests.get(f"{FASTAPI_URL}/api/health")
    print_response("FastAPI Health Check", response)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_fastapi_ingestion():
    response = requests.post(f"{FASTAPI_URL}/api/ingest")
    print_response("FastAPI Ingestion Trigger", response)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    time.sleep(1)

def test_fastapi_customers_from_db():
    # Test page 1, limit 5 from FastAPI (Postgres)
    response = requests.get(f"{FASTAPI_URL}/api/customers?page=1&limit=5")
    print_response("FastAPI DB Pagination (Page 1, Limit 5)", response)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 5
    assert data["total"] >= 20
    assert data["page"] == 1
    assert data["limit"] == 5

def test_fastapi_single_customer_from_db():
    # Get a customer ID from Flask first to know what to look for
    flask_resp = requests.get(f"{FLASK_URL}/api/customers?page=1&limit=1")
    customer_id = flask_resp.json()["data"][0]["customer_id"]
    
    response = requests.get(f"{FASTAPI_URL}/api/customers/{customer_id}")
    print_response(f"FastAPI DB Single Customer ({customer_id})", response)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id

def test_flask_404_missing_customer():
    response = requests.get(f"{FLASK_URL}/api/customers/NON-EXISTENT")
    print_response("Flask 404 Check", response)
    assert response.status_code == 404

def test_fastapi_404_missing_customer():
    response = requests.get(f"{FASTAPI_URL}/api/customers/NON-EXISTENT")
    print_response("FastAPI 404 Check", response)
    assert response.status_code == 404

if __name__ == "__main__":
    print("Running tests and displaying responses...")
    try:
        test_flask_health()
        test_flask_customers_pagination()
        test_flask_single_customer()
        test_fastapi_health()
        test_fastapi_ingestion()
        test_fastapi_customers_from_db()
        test_fastapi_single_customer_from_db()
        test_flask_404_missing_customer()
        test_fastapi_404_missing_customer()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
