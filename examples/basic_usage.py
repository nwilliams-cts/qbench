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
            base_url="https://your-qbench-instance.qbench.net",
            api_key="your-api-key",
            api_secret="your-api-secret"
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
        # Get a specific sample (now returns just the sample data by default)
        sample = qb.get_sample(1234)
        print(f"Sample 1234: {sample.get('description', 'N/A')}")
        
        # Get first page of samples (returns just the list of samples)
        samples = qb.get_samples(page_limit=1)
        print(f"Retrieved {len(samples)} samples")
        
        # If you need the full API response with metadata
        samples_with_metadata = qb.get_samples(page_limit=1, include_metadata=True)
        print(f"Total pages available: {samples_with_metadata.get('total_pages', 'Unknown')}")
        
        # Get samples with filters (returns just the list)
        active_samples = qb.get_samples(status="Completed", page_limit=2)
        print(f"Active samples: {len(active_samples)}")
        
        # Get only first 3 pages of samples
        limited_samples = qb.get_samples(page_limit=3)
        print(f"Limited samples (3 pages): {len(limited_samples)}")
        
    except QBenchAPIError as e:
        print(f"Error working with samples: {e}")


def customer_operations_example(qb):
    """Examples of working with customers."""
    try:
        # Get all customers (returns just the list)
        customers = qb.get_customers()
        print(f"Total customers: {len(customers)}")
        
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
        if customers:
            first_customer_id = customers[0]['id']
            customer = qb.get_customer(entity_id=first_customer_id)
            print(f"Customer details: {customer.get('customer_name', 'N/A')}")
            
    except QBenchAPIError as e:
        print(f"Error working with customers: {e}")


def order_operations_example(qb):
    """Examples of working with orders."""
    try:
        # Get recent orders (returns just the list)
        recent_orders = qb.get_orders(page_limit=1)
        print(f"Recent orders: {len(recent_orders)}")
        
        # Get orders for a specific customer
        orders_for_customer = qb.get_orders(customer_ids=360)
        print(f"Orders for customer 360: {len(orders_for_customer)}")
        
        # Get a specific order with its details
        if recent_orders:
            order_id = recent_orders[0]['id']
            order_details = qb.get_order(entity_id=order_id)
            print(f"Order {order_id} status: {order_details.get('state', 'Unknown')}")
            
    except QBenchAPIError as e:
        print(f"Error working with orders: {e}")


def assay_operations_example(qb):
    """Examples of working with assays."""
    try:
        # Get all assays (returns just the list)
        assays = qb.get_assays()
        print(f"Total assays: {len(assays)}")
        
        # Get active assays only
        active_assays = qb.get_assays()
        print(f"Active assays: {len(active_assays)}")
        
        # Get assay details
        if assays:
            assay_id = assays[0]['id']
            assay = qb.get_assay(entity_id=assay_id)
            print(f"Assay details: {assay.get('title', 'N/A')}")
            
            # Get assay panels
            panels = qb.get_assay_panels(entity_id=assay_id)
            print(f"Assay {assay_id} panels: {len(panels)}")
            
    except QBenchAPIError as e:
        print(f"Error working with assays: {e}")


async def async_operations_example():
    """Example of using the SDK in async context."""
    try:
        qb = qbench.connect(
            base_url="https://your-qbench-instance.qbench.net",
            api_key="your-api-key",
            api_secret="your-api-secret"
        )
        
        # In async context, these calls return coroutines
        samples = await qb.get_samples(page_limit=2)
        customers = await qb.get_customers(page_limit=2)
        
        print(f"Async - Samples: {len(samples)}, Customers: {len(customers)}")
        
        # Clean up
        qb.close()
        
    except Exception as e:
        print(f"Async error: {e}")


def v1_api_example(qb):
    """Example of using v1 API endpoints."""
    try:
        # Some data might be more accessible in v1
        v1_samples = qb.get_samples(use_v1=True, page_limit=1)
        print(f"V1 API samples: {len(v1_samples)}")
        
        # Compare with v2
        v2_samples = qb.get_samples(use_v1=False, page_limit=1)
        print(f"V2 API samples: {len(v2_samples)}")
        
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


def metadata_example(qb):
    """Example of using the include_metadata flag."""
    try:
        print("--- Metadata Examples ---")
        
        # By default, get only the data (cleaner interface)
        samples = qb.get_samples(page_limit=1)
        print(f"Default behavior - Just the data: {type(samples)} with {len(samples)} items")
        
        # Get the full response with metadata
        samples_with_metadata = qb.get_samples(page_limit=1, include_metadata=True)
        print(f"With metadata: {type(samples_with_metadata)}")
        print(f"Available keys: {list(samples_with_metadata.keys())}")
        print(f"Total pages: {samples_with_metadata.get('total_pages', 'N/A')}")
        print(f"Current page: {samples_with_metadata.get('current_page', 'N/A')}")
        
        # Same applies to single entity requests
        if samples:
            sample_id = samples[0]['id']
            
            # Get just the sample data
            sample = qb.get_sample(entity_id=sample_id)
            print(f"Single sample (default): {type(sample)}")
            
            # Get sample with full response metadata
            sample_with_metadata = qb.get_sample(entity_id=sample_id, include_metadata=True)
            print(f"Single sample (with metadata): {type(sample_with_metadata)}")
            if isinstance(sample_with_metadata, dict) and 'data' in sample_with_metadata:
                print(f"Metadata keys: {[k for k in sample_with_metadata.keys() if k != 'data']}")
                
    except QBenchAPIError as e:
        print(f"Error in metadata example: {e}")


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
        
        print("\n--- Metadata Example ---")
        metadata_example(qb)
        
    finally:
        # Clean up
        qb.close()
        print("\nConnection closed.")
    
    # Run async example
    print("\n--- Async Operations ---")
    asyncio.run(async_operations_example())


if __name__ == "__main__":
    main()
