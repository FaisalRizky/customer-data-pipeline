from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models.customer import Customer, Base
from services.ingestion import run_ingestion
from typing import List
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.delete("/api/cleanup")
def cleanup_data():
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS _dlt_loads, _dlt_pipeline_state, _dlt_version CASCADE;"))
            conn.commit()
        return {"status": "success", "message": "Database cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
def ingest_data():
    try:
        _, count = run_ingestion()
        return {"status": "success", "records_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def list_customers(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    customers = db.query(Customer).offset(skip).limit(limit).all()
    total = db.query(Customer).count()
    
    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/customers/{id}")
def get_customer(id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
