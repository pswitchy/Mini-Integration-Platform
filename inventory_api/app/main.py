import uuid
from datetime import datetime, timezone
from typing import List, Literal
from fastapi import FastAPI, status
from pydantic import BaseModel, Field

class PackageRequestCreate(BaseModel):
    customer_id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    package_type: str = Field("welcome_package", example="welcome_package")

class PackageRequest(PackageRequestCreate):
    request_id: uuid.UUID = Field(..., example="e1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6")
    status: Literal["pending", "shipped", "delivered"] = "pending"
    created_at: datetime = Field(..., example="2023-01-01T12:01:00Z")

db_requests: List[PackageRequest] = []

app = FastAPI(
    title="Mock Inventory API",
    description="A mock API for managing package requests.",
    version="1.0.0"
)

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