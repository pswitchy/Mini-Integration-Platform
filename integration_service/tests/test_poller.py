import pytest
import respx
from httpx import Response
from service import poller

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
    poller.processed_customer_ids.clear()

    crm_route = mock_apis.get(f"{poller.CRM_API_URL}").mock(
        return_value=Response(200, json=MOCK_CRM_RESPONSE)
    )

    inventory_route = mock_apis.post(f"{poller.INVENTORY_API_URL}").mock(
        return_value=Response(201)
    )

    customers = poller.fetch_customers()
    for customer in customers:
        customer_id = customer.get("id")
        if customer_id and customer_id not in poller.processed_customer_ids:
            if poller.create_package_request(customer_id):
                poller.processed_customer_ids.add(customer_id)

    assert crm_route.called
    assert inventory_route.call_count == 2

    first_call_payload = inventory_route.calls[0].request.content
    second_call_payload = inventory_route.calls[1].request.content
    
    assert b'"customer_id": "c3e8e5a6-3d7c-4c6c-8f3e-4d4b1a1b1a1a"' in first_call_payload
    assert b'"customer_id": "b2a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"' in second_call_payload
    
    assert len(poller.processed_customer_ids) == 2


def test_does_not_process_existing_customer(mock_apis):
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

    assert inventory_route.call_count == 1
    call_payload = inventory_route.calls.last.request.content
    assert b'"customer_id": "b2a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"' in call_payload
    assert len(poller.processed_customer_ids) == 2