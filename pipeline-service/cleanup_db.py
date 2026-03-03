from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_db")

def cleanup():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Cleaning up 'customers' table...")
        conn.execute(text("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;"))
        
        print("Cleaning up dlt internal tables...")
        conn.execute(text("DROP TABLE IF EXISTS _dlt_loads, _dlt_pipeline_state, _dlt_version CASCADE;"))
        
        conn.commit()
    print("Database cleanup successful.")

if __name__ == "__main__":
    try:
        cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")
