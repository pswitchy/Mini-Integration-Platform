# Mini Integration Platform

This project demonstrates a lightweight integration between a mock CRM system and a mock Inventory system. When a new customer is created in the CRM, a corresponding "welcome package" request is automatically created in the Inventory system.

This project is built using Python (FastAPI), Docker, and Docker Compose, and it includes demonstrations of key integration concepts like polling, error handling, logging, and unit testing.

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
