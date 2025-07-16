"""
Basic QBench SDK usage examples.

This file demonstrates common usage patterns for the QBench SDK.
"""

import qbench
import asyncio
from qbench.exceptions import QBenchAPIError, QBenchAuthError


def basic_connection_example():
    """Basic connection and health check example."""
    try:
        # Connect to QBench
        qb = qbench.connect(
            base_url="https://your-qbench-instance.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        
        # Perform health check
        health = qb.health_check()
        print(f"Health check: {health}")
        
        # List available endpoints
        endpoints = qb.list_available_endpoints()
        print(f"Available endpoints: {len(endpoints)}")
        
        return qb
        
    except QBenchAuthError as e:
        print(f"Authentication failed: {e}")
        return None
    except QBenchAPIError as e:
        print(f"API error: {e}")
        return None


def sample_operations_example(qb):
    """Examples of working with samples."""
    try:
        # Get a specific sample
        sample = qb.get_sample(entity_id=1234)
        print(f"Sample 1234: {sample.get('name', 'N/A')}")
        
        # Get all samples (paginated automatically)
        all_samples = qb.get_samples()
        print(f"Total samples: {len(all_samples['data'])}")
        
        # Get samples with filters
        active_samples = qb.get_samples(status="active", limit=10)
        print(f"Active samples: {len(active_samples['data'])}")
        
        # Get only first 3 pages of samples
        limited_samples = qb.get_samples(page_limit=3)
        print(f"Limited samples (3 pages): {len(limited_samples['data'])}")
        
    except QBenchAPIError as e:
        print(f"Error working with samples: {e}")


def customer_operations_example(qb):
    """Examples of working with customers."""
    try:
        # Get all customers
        customers = qb.get_customers()
        print(f"Total customers: {len(customers['data'])}")
        
        # Create a new customer
        new_customer_data = {
            "name": "ACME Corporation",
            "email": "contact@acme.com",
            "phone": "555-0123"
        }
        
        # Note: Uncomment to actually create
        # new_customer = qb.create_customers(data=new_customer_data)
        # print(f"Created customer: {new_customer}")
        
        # Get a specific customer
        if customers['data']:
            first_customer_id = customers['data'][0]['id']
            customer = qb.get_customer(entity_id=first_customer_id)
            print(f"Customer details: {customer.get('name', 'N/A')}")
            
    except QBenchAPIError as e:
        print(f"Error working with customers: {e}")


def order_operations_example(qb):
    """Examples of working with orders."""
    try:
        # Get recent orders
        recent_orders = qb.get_orders(limit=20)
        print(f"Recent orders: {len(recent_orders['data'])}")
        
        # Get orders for a specific customer
        orders_for_customer = qb.get_orders(customer_id=123)
        print(f"Orders for customer 123: {len(orders_for_customer['data'])}")
        
        # Get a specific order with its details
        if recent_orders['data']:
            order_id = recent_orders['data'][0]['id']
            order_details = qb.get_order(entity_id=order_id)
            print(f"Order {order_id} status: {order_details.get('status', 'Unknown')}")
            
    except QBenchAPIError as e:
        print(f"Error working with orders: {e}")


def assay_operations_example(qb):
    """Examples of working with assays."""
    try:
        # Get all assays
        assays = qb.get_assays()
        print(f"Total assays: {len(assays['data'])}")
        
        # Get active assays only
        active_assays = qb.get_assays(active=True)
        print(f"Active assays: {len(active_assays['data'])}")
        
        # Get assay details
        if assays['data']:
            assay_id = assays['data'][0]['id']
            assay = qb.get_assay(entity_id=assay_id)
            print(f"Assay details: {assay.get('name', 'N/A')}")
            
            # Get assay panels
            panels = qb.get_assay_panels(entity_id=assay_id)
            print(f"Assay {assay_id} panels: {len(panels['data'])}")
            
    except QBenchAPIError as e:
        print(f"Error working with assays: {e}")


async def async_operations_example():
    """Example of using the SDK in async context."""
    try:
        qb = qbench.connect(
            base_url="https://your-qbench-instance.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        
        # In async context, these calls return coroutines
        samples = await qb.get_samples(limit=10)
        customers = await qb.get_customers(limit=10)
        
        print(f"Async - Samples: {len(samples['data'])}, Customers: {len(customers['data'])}")
        
        # Clean up
        qb.close()
        
    except Exception as e:
        print(f"Async error: {e}")


def v1_api_example(qb):
    """Example of using v1 API endpoints."""
    try:
        # Some data might be more accessible in v1
        v1_samples = qb.get_samples(use_v1=True, limit=5)
        print(f"V1 API samples: {len(v1_samples['data'])}")
        
        # Compare with v2
        v2_samples = qb.get_samples(use_v1=False, limit=5)
        print(f"V2 API samples: {len(v2_samples['data'])}")
        
    except QBenchAPIError as e:
        print(f"Error with v1 API: {e}")


def error_handling_example(qb):
    """Example of proper error handling."""
    try:
        # Try to get a non-existent sample
        sample = qb.get_sample(entity_id=999999)
        
    except QBenchAPIError as e:
        print(f"API Error: {e}")
        if e.status_code == 404:
            print("Sample not found")
        elif e.status_code == 401:
            print("Authentication issue")
        else:
            print(f"Other API error: {e.status_code}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    """Main example runner."""
    print("QBench SDK Examples")
    print("=" * 50)
    
    # Basic connection
    qb = basic_connection_example()
    if not qb:
        print("Failed to connect to QBench. Check your credentials.")
        return
    
    try:
        # Run examples
        print("\n--- Sample Operations ---")
        sample_operations_example(qb)
        
        print("\n--- Customer Operations ---")
        customer_operations_example(qb)
        
        print("\n--- Order Operations ---")
        order_operations_example(qb)
        
        print("\n--- Assay Operations ---")
        assay_operations_example(qb)
        
        print("\n--- V1 API Example ---")
        v1_api_example(qb)
        
        print("\n--- Error Handling Example ---")
        error_handling_example(qb)
        
    finally:
        # Clean up
        qb.close()
        print("\nConnection closed.")
    
    # Run async example
    print("\n--- Async Operations ---")
    asyncio.run(async_operations_example())


if __name__ == "__main__":
    main()
