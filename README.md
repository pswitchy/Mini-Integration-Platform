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
