import os
import time
import logging
import requests

CRM_API_URL = os.getenv("CRM_API_URL", "http://localhost:8000/customers")
INVENTORY_API_URL = os.getenv("INVENTORY_API_URL", "http://localhost:8001/package-requests")
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", 10))
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

processed_customer_ids = set()

def fetch_customers():
    """Fetches all customers from the CRM API with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            logging.info("Attempting to fetch customers from CRM...")
            response = requests.get(CRM_API_URL, timeout=5)
            response.raise_for_status()  
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
                        processed_customer_ids.add(customer_id)
            
            if new_customer_count == 0:
                logging.info("No new customers found.")
        else:
            logging.warning("Skipping processing cycle due to CRM API fetch failure.")

        logging.info(f"--- Polling cycle finished. Waiting for {POLLING_INTERVAL_SECONDS} seconds. ---")
        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()