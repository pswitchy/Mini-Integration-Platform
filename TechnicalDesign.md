# Technical Design Document: Mini Integration Platform

## 1. Overview

This document outlines the technical architecture, data flow, and design decisions for the Mini Integration Platform. The goal is to create a reliable, observable, and simple integration between a mock CRM and a mock Inventory system.

The core scenario is: **When a new customer is added to the CRM, a "welcome package" request is created in the Inventory system.**

## 2. System Architecture

The system consists of three independent components running as Docker containers, orchestrated by Docker Compose.

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