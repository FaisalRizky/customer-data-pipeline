import dlt
import requests
import os
from datetime import datetime

FLASK_API_URL = os.getenv("FLASK_API_URL", "http://mock-server:5000/api/customers")

@dlt.resource(name="customers", write_disposition="merge", primary_key="customer_id")
def fetch_customers():
    page = 1
    limit = 10
    total_processed = 0
    
    while True:
        url = f"{FLASK_API_URL}?page={page}&limit={limit}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        customers = data.get("data", [])
        if not customers:
            break
            
        for c in customers:
            if c.get("date_of_birth"):
                try:
                    c["date_of_birth"] = datetime.strptime(c["date_of_birth"], "%Y-%m-%d").date()
                except:
                    pass
            if c.get("created_at"):
                try:
                    c["created_at"] = datetime.strptime(c["created_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                except:
                    pass

        yield customers
        
        total_processed += len(customers)
        if total_processed >= data.get("total", 0):
            break
        
        page += 1

def run_ingestion():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/customer_db")
    
    pipeline = dlt.pipeline(
        pipeline_name="customer_ingestion",
        destination="postgres",
        dataset_name="public",
        credentials=database_url
    )
    
    all_records = list(fetch_customers())
    total_count = len(all_records)
    
    info = pipeline.run(all_records, table_name="customers")
    
    return info, total_count
