import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

class CustomerCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")

class Customer(CustomerCreate):
    id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    created_at: datetime = Field(..., example="2023-01-01T12:00:00Z")

db_customers: List[Customer] = []

app = FastAPI(
    title="Mock CRM API",
    description="A mock API for managing customers.",
    version="1.0.0"
)

@app.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer_in: CustomerCreate):
    """
    Adds a new customer to the system.
    """
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