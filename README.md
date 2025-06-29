Of course. This is an excellent pre-interview project that tests a wide range of practical skills. Here is a complete, well-structured solution that you can use as a reference or submit directly. It covers all requirements, including the optional ones.

Project Overview

This project implements a mini integration platform with three core components:

CRM API: A mock service for managing customers.

Inventory API: A mock service for managing "welcome package" requests.

Integration Service: A polling service that checks for new customers in the CRM and creates corresponding package requests in the Inventory system.

The entire system is containerized using Docker and orchestrated with Docker Compose for easy setup and demonstration of cloud-native principles.

File Structure

Here is the recommended file structure for the project. It's organized for clarity, scalability, and separation of concerns.

Generated code
mini-integration-platform/
├── crm_api/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── Dockerfile
├── inventory_api/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── Dockerfile
├── integration_service/
│   ├── service/
│   │   ├── __init__.py
│   │   └── poller.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_poller.py
│   └── Dockerfile
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── README.md
└── TECHNICAL_DESIGN.md

1. Root-Level Files

These files are at the root of the project and manage the overall environment and documentation.

requirements.txt

This file lists all Python dependencies for all services.

Generated txt
# Fast API for our mock APIs
fastapi==0.104.1
uvicorn[standard]==0.24.0.post1
pydantic==2.5.2

# For the integration service and tests
requests==2.31.0

# For testing
pytest==7.4.3
httpx==0.25.1 # Used by FastAPI's TestClient and good for mocking
respx==0.20.2 # A utility for mocking httpx requests
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Txt
IGNORE_WHEN_COPYING_END
docker-compose.yml

This file orchestrates the three services, making it easy to run the entire platform with a single command. It handles networking, environment variables, and dependencies between services.

Generated yaml
version: '3.8'

services:
  crm_api:
    build:
      context: ./crm_api
    ports:
      - "8000:80"
    volumes:
      - ./crm_api/app:/code/app
    container_name: crm_api

  inventory_api:
    build:
      context: ./inventory_api
    ports:
      - "8001:80"
    volumes:
      - ./inventory_api/app:/code/app
    container_name: inventory_api

  integration_service:
    build:
      context: ./integration_service
    environment:
      - CRM_API_URL=http://crm_api/customers
      - INVENTORY_API_URL=http://inventory_api/package-requests
      - POLLING_INTERVAL_SECONDS=10
    depends_on:
      - crm_api
      - inventory_api
    volumes:
      - ./integration_service/service:/code/service
    container_name: integration_service
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Yaml
IGNORE_WHEN_COPYING_END
.gitignore

A standard gitignore file for Python projects.

Generated code
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.pytest_cache/
.hypothesis/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE files
.idea/
.vscode/
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
2. Mock API: CRM Service
crm_api/Dockerfile
Generated dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /code/app

# Command to run the application
# Uvicorn will run on port 80 inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Dockerfile
IGNORE_WHEN_COPYING_END
crm_api/app/main.py

This is the FastAPI application for the CRM. It uses an in-memory list as a mock database.

Generated python
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

# --- Pydantic Models ---
class CustomerCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")

class Customer(CustomerCreate):
    id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    created_at: datetime = Field(..., example="2023-01-01T12:00:00Z")

# --- Mock Database ---
# A simple in-memory list to store customers
db_customers: List[Customer] = []

# --- FastAPI App ---
app = FastAPI(
    title="Mock CRM API",
    description="A mock API for managing customers.",
    version="1.0.0"
)

# --- API Endpoints ---
@app.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer_in: CustomerCreate):
    """
    Adds a new customer to the system.
    """
    # Check for duplicate email
    if any(c.email == customer_in.email for c in db_customers):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with email '{customer_in.email}' already exists."
        )

    new_customer = Customer(
        id=uuid.uuid4(),
        name=customer_in.name,
        email=customer_in.email,
        created_at=datetime.now(timezone.utc)
    )
    db_customers.append(new_customer)
    print(f"CRM_API: Added new customer: {new_customer.name} ({new_customer.id})")
    return new_customer

@app.get("/customers", response_model=List[Customer])
def get_all_customers():
    """
    Retrieves a list of all customers.
    """
    return db_customers

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mock CRM API"}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
3. Mock API: Inventory Service
inventory_api/Dockerfile

(Identical to the CRM Dockerfile)

Generated dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /code/app

# Command to run the application
# Uvicorn will run on port 80 inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Dockerfile
IGNORE_WHEN_COPYING_END
inventory_api/app/main.py

FastAPI application for the Inventory system.

Generated python
import uuid
from datetime import datetime, timezone
from typing import List, Literal
from fastapi import FastAPI, status
from pydantic import BaseModel, Field

# --- Pydantic Models ---
class PackageRequestCreate(BaseModel):
    customer_id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    package_type: str = Field("welcome_package", example="welcome_package")

class PackageRequest(PackageRequestCreate):
    request_id: uuid.UUID = Field(..., example="e1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6")
    status: Literal["pending", "shipped", "delivered"] = "pending"
    created_at: datetime = Field(..., example="2023-01-01T12:01:00Z")

# --- Mock Database ---
db_requests: List[PackageRequest] = []

# --- FastAPI App ---
app = FastAPI(
    title="Mock Inventory API",
    description="A mock API for managing package requests.",
    version="1.0.0"
)

# --- API Endpoints ---
@app.post("/package-requests", response_model=PackageRequest, status_code=status.HTTP_201_CREATED)
def create_package_request(request_in: PackageRequestCreate):
    """
    Creates a new package request for a customer.
    """
    new_request = PackageRequest(
        request_id=uuid.uuid4(),
        customer_id=request_in.customer_id,
        package_type=request_in.package_type,
        created_at=datetime.now(timezone.utc)
    )
    db_requests.append(new_request)
    print(f"INVENTORY_API: Created package request for customer: {new_request.customer_id}")
    return new_request

@app.get("/package-requests", response_model=List[PackageRequest])
def get_all_package_requests():
    """
    Retrieves a list of all package requests.
    """
    return db_requests
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Mock Inventory API"}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
4. Integration Service

This component contains the core integration logic.

integration_service/Dockerfile
Generated dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./service /code/service

# Command to run the integration service script
CMD ["python", "service/poller.py"]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Dockerfile
IGNORE_WHEN_COPYING_END
integration_service/service/poller.py

This script polls the CRM, finds new customers, and creates package requests in the Inventory system. It includes logging, error handling, and simple retry logic.

Generated python
import os
import time
import logging
import requests

# --- Configuration ---
CRM_API_URL = os.getenv("CRM_API_URL", "http://localhost:8000/customers")
INVENTORY_API_URL = os.getenv("INVENTORY_API_URL", "http://localhost:8001/package-requests")
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", 10))
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- State ---
# In a real application, this would be a persistent store like Redis or a database.
# For this project, an in-memory set is sufficient.
processed_customer_ids = set()

def fetch_customers():
    """Fetches all customers from the CRM API with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            logging.info("Attempting to fetch customers from CRM...")
            response = requests.get(CRM_API_URL, timeout=5)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            logging.info("Successfully fetched customers.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch customers (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS)
    return None

def create_package_request(customer_id: str):
    """Creates a welcome package request in the Inventory API."""
    payload = {"customer_id": customer_id, "package_type": "welcome_package"}
    try:
        logging.info(f"Creating package request for customer ID: {customer_id}")
        response = requests.post(INVENTORY_API_URL, json=payload, timeout=5)
        response.raise_for_status()
        logging.info(f"Successfully created package request for customer ID: {customer_id}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to create package request for customer ID {customer_id}: {e}")
        return False

def main_loop():
    """The main polling loop for the integration service."""
    logging.info("Integration service started.")
    while True:
        logging.info("--- Polling cycle started ---")
        customers = fetch_customers()

        if customers is not None:
            new_customer_count = 0
            for customer in customers:
                customer_id = customer.get("id")
                if customer_id and customer_id not in processed_customer_ids:
                    new_customer_count += 1
                    logging.info(f"Found new customer: {customer.get('name')} (ID: {customer_id})")
                    if create_package_request(customer_id):
                        # Only mark as processed if the inventory call was successful
                        processed_customer_ids.add(customer_id)
            
            if new_customer_count == 0:
                logging.info("No new customers found.")
        else:
            logging.warning("Skipping processing cycle due to CRM API fetch failure.")

        logging.info(f"--- Polling cycle finished. Waiting for {POLLING_INTERVAL_SECONDS} seconds. ---")
        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
integration_service/tests/test_poller.py

Unit tests for the most critical part of the system: the poller logic. This uses respx to mock HTTP calls.

Generated python
import pytest
import respx
from httpx import Response
from service import poller

# Sample customer data from CRM API
MOCK_CRM_RESPONSE = [
    {
        "name": "Alice",
        "email": "alice@example.com",
        "id": "c3e8e5a6-3d7c-4c6c-8f3e-4d4b1a1b1a1a",
        "created_at": "2023-10-27T10:00:00Z"
    },
    {
        "name": "Bob",
        "email": "bob@example.com",
        "id": "b2a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5",
        "created_at": "2023-10-27T11:00:00Z"
    }
]

@pytest.fixture
def mock_apis():
    with respx.mock(base_url="http://test") as mock:
        yield mock

def test_finds_new_customer_and_creates_package_request(mock_apis):
    # Arrange: Reset the state for the test
    poller.processed_customer_ids.clear()
    
    # Mock the CRM API endpoint
    crm_route = mock_apis.get(f"{poller.CRM_API_URL}").mock(
        return_value=Response(200, json=MOCK_CRM_RESPONSE)
    )
    
    # Mock the Inventory API endpoint
    inventory_route = mock_apis.post(f"{poller.INVENTORY_API_URL}").mock(
        return_value=Response(201)
    )

    # Act: Run one cycle of fetching and processing
    customers = poller.fetch_customers()
    for customer in customers:
        customer_id = customer.get("id")
        if customer_id and customer_id not in poller.processed_customer_ids:
            if poller.create_package_request(customer_id):
                poller.processed_customer_ids.add(customer_id)

    # Assert
    assert crm_route.called
    assert inventory_route.call_count == 2
    
    # Check that package requests were made for both customers
    first_call_payload = inventory_route.calls[0].request.content
    second_call_payload = inventory_route.calls[1].request.content
    
    assert b'"customer_id": "c3e8e5a6-3d7c-4c6c-8f3e-4d4b1a1b1a1a"' in first_call_payload
    assert b'"customer_id": "b2a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"' in second_call_payload
    
    assert len(poller.processed_customer_ids) == 2


def test_does_not_process_existing_customer(mock_apis):
    # Arrange: Pretend 'Alice' has already been processed
    poller.processed_customer_ids.clear()
    poller.processed_customer_ids.add("c3e8e5a6-3d7c-4c6c-8f3e-4d4b1a1b1a1a")

    crm_route = mock_apis.get(f"{poller.CRM_API_URL}").mock(
        return_value=Response(200, json=MOCK_CRM_RESPONSE)
    )
    inventory_route = mock_apis.post(f"{poller.INVENTORY_API_URL}").mock(
        return_value=Response(201)
    )

    # Act
    customers = poller.fetch_customers()
    for customer in customers:
        customer_id = customer.get("id")
        if customer_id and customer_id not in poller.processed_customer_ids:
            if poller.create_package_request(customer_id):
                poller.processed_customer_ids.add(customer_id)

    # Assert: Inventory API should only be called for 'Bob'
    assert inventory_route.call_count == 1
    call_payload = inventory_route.calls.last.request.content
    assert b'"customer_id": "b2a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"' in call_payload
    assert len(poller.processed_customer_ids) == 2
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
5. Documentation

These files explain the "what," "how," and "why" of the project.

README.md
Generated markdown
# Mini Integration Platform

This project demonstrates a lightweight integration between a mock CRM system and a mock Inventory system. When a new customer is created in the CRM, a corresponding "welcome package" request is automatically created in the Inventory system.

This project is built using Python (FastAPI), Docker, and Docker Compose, and it includes demonstrations of key integration concepts like polling, error handling, logging, and unit testing.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
- [How to Use](#how-to-use)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)

## Features

- **Mock CRM API**: Add and view customers.
- **Mock Inventory API**: Create and list package requests.
- **Integration Service**: A polling service that detects new customers and triggers inventory actions.
- **Containerized**: All services are containerized with Docker for easy and consistent setup.
- **Orchestrated**: `docker-compose` manages the entire application stack.
- **Error Handling**: The integration service includes retry logic for API calls.
- **Logging**: The integration service provides clear logs about its activities.
- **Unit Tests**: Key integration logic is covered by unit tests.

## Architecture

For a detailed explanation of the architecture, data flow, and design decisions, please see the [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) file.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## How to Run

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd mini-integration-platform
    ```

2.  **Build and run the services using Docker Compose:**
    ```sh
    docker-compose up --build
    ```

This command will build the Docker images for all three services and start them. You will see interleaved logs from the CRM API, Inventory API, and the Integration Service in your terminal.

- The **CRM API** will be available at `http://localhost:8000`
- The **Inventory API** will be available at `http://localhost:8001`
- The **Integration Service** will start polling in the background.

## How to Use

1.  **Add a new customer to the CRM:**
    You can use a tool like `curl` or Postman to send a `POST` request.

    ```sh
    curl -X POST "http://localhost:8000/customers" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Jane Doe",
      "email": "jane.doe@example.com"
    }'
    ```

2.  **Observe the integration service:**
    Within 10 seconds (the default polling interval), you will see logs in your `docker-compose` terminal indicating that the integration service has found the new customer and created a package request.

    ```
    integration_service | INFO: Found new customer: Jane Doe (ID: <uuid>)
    integration_service | INFO: Creating package request for customer ID: <uuid>
    inventory_api       | INVENTORY_API: Created package request for customer: <uuid>
    integration_service | INFO: Successfully created package request for customer ID: <uuid>
    ```

3.  **Verify the package request in the Inventory system:**
    You can list all package requests to confirm it was created.

    ```sh
    curl http://localhost:8001/package-requests
    ```
    You should see the new welcome package request in the JSON response.

## Running Tests

The unit tests for the integration service's poller logic can be run within its container.

1.  First, ensure the services are running with `docker-compose up`.
2.  In a new terminal, open a shell into the `integration_service` container:
    ```sh
    docker-compose exec integration_service sh
    ```
3.  Inside the container's shell, run pytest:
    ```sh
    # The working directory is /code
    pytest
    ```

## API Documentation

Both the CRM and Inventory APIs come with automatically generated OpenAPI (Swagger) documentation. Once the services are running, you can access them in your browser:

- **CRM API Docs**: `http://localhost:8000/docs`
- **Inventory API Docs**: `http://localhost:8001/docs`
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Markdown
IGNORE_WHEN_COPYING_END
TECHNICAL_DESIGN.md
Generated markdown
# Technical Design Document: Mini Integration Platform

## 1. Overview

This document outlines the technical architecture, data flow, and design decisions for the Mini Integration Platform. The goal is to create a reliable, observable, and simple integration between a mock CRM and a mock Inventory system.

The core scenario is: **When a new customer is added to the CRM, a "welcome package" request is created in the Inventory system.**

## 2. System Architecture

The system consists of three independent components running as Docker containers, orchestrated by Docker Compose.
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Markdown
IGNORE_WHEN_COPYING_END

+--------------------------------------------------------------------------+
| Your Machine |
| (Docker Host) |
| |
| +-----------------+ +-------------------------+ +-------------------+ |
| | CRM API | | Integration Service | | Inventory API | |
| | (Container) |<------->| (Container) |<------>| (Container) | |
| | Port: 8000 | | (Polling Logic) | | Port: 8001 | |
| +-----------------+ +-------------------------+ +-------------------+ |
| ^ ^ ^ ^ |
| | | | | |
| User interacts via HTTP ---+ | | | |
| | | | |
+------------------------------------+----------+------------------------+-----------+
| |
| |
Reads new customer data -----+ +---- Creates package request

Generated code
### 2.1. Components

-   **CRM API**: A RESTful API built with Python/FastAPI. It exposes endpoints to create and list customers. It uses a simple in-memory list as its data store.
-   **Inventory API**: A RESTful API built with Python/FastAPI. It exposes endpoints to create and list package requests. It also uses an in-memory data store.
-   **Integration Service**: A standalone Python script that acts as the "middleware." It implements a polling integration pattern to connect the two APIs.

## 3. Integration Pattern: Polling

For this project, a **polling** mechanism was chosen for its simplicity and effectiveness in this scenario.

### 3.1. Data Flow

1.  **Start**: The Integration Service starts and initializes an empty set of `processed_customer_ids`.
2.  **Poll**: Every 10 seconds, the service calls the `GET /customers` endpoint on the CRM API.
3.  **Diff**: It iterates through the list of customers received from the CRM. For each customer, it checks if the customer's ID is in its `processed_customer_ids` set.
4.  **Action**: If a customer ID is *not* in the set, the service considers it a "new" customer.
    -   It makes a `POST /package-requests` call to the Inventory API, providing the new customer's ID.
    -   If the call to the Inventory API is successful (e.g., HTTP 201 Created), it adds the customer's ID to the `processed_customer_ids` set.
5.  **Repeat**: The service waits for the polling interval and starts the cycle again at step 2.

### 3.2. Rationale for Polling

-   **Simplicity**: It's easy to implement and understand. It does not require changes to the source system (CRM) to push events.
-   **Decoupling**: The CRM and Inventory APIs remain completely independent. The CRM doesn't need to know that an Inventory system exists.
-   **Resilience**: If the Inventory API is down, the poller will fail to create the package request. Since the customer ID is not added to the processed set, the service will automatically retry on the next polling cycle.

### 3.3. Alternative: Webhooks / Event-Driven

A more advanced, real-time alternative would be a **webhook** or **event-driven** pattern.

-   **Flow**: The CRM API's `POST /customers` endpoint, after successfully saving a customer, would directly push an event (e.g., a JSON payload with customer details) to a message queue (like RabbitMQ, SQS) or a webhook endpoint on the integration service.
-   **Pros**: Real-time, more efficient (no empty polls), and scales better.
-   **Cons**: Tighter coupling (the CRM must be configured to call the webhook), and more complex infrastructure (requires a webhook receiver or a message broker).

For the scope of this project, polling is a perfectly valid and robust choice.

## 4. Error Handling and Resilience (Bonus)

-   **API Unavailability**: The integration service uses a `try...except` block when making HTTP requests to the CRM and Inventory APIs. If an API is down or returns an error, the service logs the error and continues.
-   **Retry Logic**: When fetching customers from the CRM, a simple retry mechanism (`MAX_RETRIES = 3`) is implemented. This handles transient network issues.
-   **Idempotency**: The use of the `processed_customer_ids` set prevents the creation of duplicate package requests, even if the service restarts (note: for a real app, this set would need to be persisted).

## 5. Cloud & DevOps Awareness

### 5.1. Containerization (Docker)

-   Each service has its own `Dockerfile`, creating a lightweight, reproducible environment.
-   `docker-compose.yml` orchestrates the entire application, defining services, networking, ports, and environment variables. This mimics how microservices are managed in cloud environments like Kubernetes.
-   **Benefit**: Developers can run the entire system with a single command (`docker-compose up`), ensuring consistency between development and production.

### 5.2. Cloud Function Deployment (e.g., AWS Lambda)

This integration logic is a prime candidate for a serverless cloud function. Here's how it would work in AWS:

1.  **Trigger**: The CRM API would be modified. Instead of just saving a customer, its `POST /customers` function would also publish a message to an **Amazon SQS (Simple Queue Service)** queue or an **SNS (Simple Notification Service)** topic. The message would contain the new customer's details.
2.  **Lambda Function**: An **AWS Lambda** function would be created with the core logic from `poller.py` (the part that creates the package request). This Lambda function would be configured to be triggered by new messages in the SQS queue.
3.  **Execution**: When a new customer is created, the message appears in SQS, which automatically invokes the Lambda function. The function receives the customer data, calls the Inventory API, and completes.

**Advantages of this approach:**
-   **Event-Driven**: Truly real-time and efficient.
-   **Serverless**: No need to manage a constantly running server/container for the polling service.
-   **Scalability**: AWS automatically scales the number of Lambda invocations based on the number of incoming events.
-   **Cost-Effective**: You only pay for the compute time when the function is actually running.
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
