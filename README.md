# Backend Developer Technical Assessment

This project implements a data pipeline consisting of a Flask Mock Server, a FastAPI Ingestion Pipeline, and a PostgreSQL database.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)

## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/
│   │   └── customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/
    │   └── customer.py
    ├── services/
    │   └── ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Getting Started

1.  **Clone the repository** (if applicable) and navigate to the project root.
2.  **Start the services** using Docker Compose:
    ```bash
    docker-compose up -d --build
    ```
3.  **Verify the services** are running:
    ```bash
    docker-compose ps
    ```

## Endpoints

### Flask Mock Server (Port 5000)
- `GET /api/health`: Health check.
- `GET /api/customers?page=1&limit=10`: Paginated list of customers.
- `GET /api/customers/{id}`: Retrieval of a single customer.

### FastAPI Pipeline Service (Port 8000)
- `GET /api/health`: Health check.
- `POST /api/ingest`: Triggers data ingestion from the Flask server to PostgreSQL.
- `GET /api/customers?page=1&limit=10`: Paginated list of customers from the database.
- `GET /api/customers/{id}`: Retrieval of a single customer from the database.

### Cleanup
To reset the database state (truncate `customers` and reset `dlt` state):

**Option 1: API Endpoint**
```bash
curl -X DELETE http://localhost:8000/api/cleanup
```

**Option 2: Python Script**
```bash
# Run from host (if SQLAlchemy is installed)
python3 pipeline-service/cleanup_db.py

# Or run via docker
docker exec pipeline_service python cleanup_db.py
```

## Testing

### Automated Test Suite
A comprehensive test suite is provided in `pipeline-service/test_endpoints.py`.

**To run from host:**
```bash
python3 pipeline-service/test_endpoints.py
```

**To run via docker:**
```bash
docker exec pipeline_service python test_endpoints.py
```

### Manual Verification
#### 1. Test Flask Mock Server
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
```

#### 2. Ingest Data
```bash
curl -X POST http://localhost:8000/api/ingest
```

#### 3. Verify Data in FastAPI
```bash
curl "http://localhost:8000/api/customers?page=1&limit=5"
```

## Implementation Details

- **Flask Mock Server**: Serves data from a static JSON file with pagination logic.
- **FastAPI Pipeline**: Uses the `dlt` library to handle data ingestion and upserts into PostgreSQL.
- **PostgreSQL**: Stores customer data with a schema defined using SQLAlchemy.
