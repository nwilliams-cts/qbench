"""
Advanced QBench SDK usage examples.

This file demonstrates more complex usage patterns including
batch operations, data processing, and integration patterns.
"""

import qbench
import asyncio
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from qbench.exceptions import QBenchAPIError


class QBenchDataProcessor:
    """Helper class for processing QBench data."""
    
    def __init__(self, qb_client):
        self.qb = qb_client
    
    async def bulk_sample_status_update(self, sample_ids: List[int], new_status: str):
        """
        Update status for multiple samples concurrently.
        
        Args:
            sample_ids: List of sample IDs to update
            new_status: New status to set
        """
        async def update_sample(sample_id):
            try:
                return await self.qb.update_samples(
                    entity_id=sample_id,
                    data={"status": new_status}
                )
            except QBenchAPIError as e:
                print(f"Failed to update sample {sample_id}: {e}")
                return None
        
        # Update samples concurrently
        tasks = [update_sample(sid) for sid in sample_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        print(f"Successfully updated {successful}/{len(sample_ids)} samples")
        
        return results
    
    def export_samples_to_csv(self, filename: str, filters: Dict[str, Any] = None):
        """
        Export samples to CSV file.
        
        Args:
            filename: Output CSV filename
            filters: Optional filters for samples
        """
        try:
            # Get all samples with filters
            samples_data = self.qb.get_samples(**(filters or {}))
            samples = samples_data.get('data', [])
            
            if not samples:
                print("No samples found to export")
                return
            
            # Get all unique keys from samples for CSV headers
            all_keys = set()
            for sample in samples:
                all_keys.update(sample.keys())
            
            headers = sorted(all_keys)
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for sample in samples:
                    # Handle nested objects by converting to JSON strings
                    row = {}
                    for key in headers:
                        value = sample.get(key, '')
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                        row[key] = value
                    writer.writerow(row)
            
            print(f"Exported {len(samples)} samples to {filename}")
            
        except Exception as e:
            print(f"Error exporting samples: {e}")
    
    def generate_sample_report(self, date_range_days: int = 30):
        """
        Generate a comprehensive sample report.
        
        Args:
            date_range_days: Number of days to look back for samples
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range_days)
            
            # Get samples in date range
            samples_data = self.qb.get_samples(
                created_after=start_date.isoformat(),
                created_before=end_date.isoformat()
            )
            samples = samples_data.get('data', [])
            
            # Generate report
            report = {
                'report_date': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': date_range_days
                },
                'summary': {
                    'total_samples': len(samples),
                    'status_breakdown': {},
                    'customer_breakdown': {},
                    'assay_breakdown': {}
                }
            }
            
            # Analyze samples
            for sample in samples:
                # Status breakdown
                status = sample.get('status', 'unknown')
                report['summary']['status_breakdown'][status] = \
                    report['summary']['status_breakdown'].get(status, 0) + 1
                
                # Customer breakdown
                customer_id = sample.get('customer_id')
                if customer_id:
                    report['summary']['customer_breakdown'][customer_id] = \
                        report['summary']['customer_breakdown'].get(customer_id, 0) + 1
                
                # Assay breakdown
                assay_id = sample.get('assay_id')
                if assay_id:
                    report['summary']['assay_breakdown'][assay_id] = \
                        report['summary']['assay_breakdown'].get(assay_id, 0) + 1
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None


async def batch_operations_example():
    """Example of batch operations and concurrent processing."""
    
    qb = qbench.connect(
        base_url="https://your-qbench-instance.com",
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    
    processor = QBenchDataProcessor(qb)
    
    try:
        # Example 1: Concurrent data fetching
        print("Fetching data concurrently...")
        
        # Fetch multiple types of data concurrently
        samples_task = qb.get_samples(limit=50)
        customers_task = qb.get_customers(limit=20)
        orders_task = qb.get_orders(limit=30)
        assays_task = qb.get_assays()
        
        samples, customers, orders, assays = await asyncio.gather(
            samples_task, customers_task, orders_task, assays_task
        )
        
        print(f"Fetched: {len(samples['data'])} samples, "
              f"{len(customers['data'])} customers, "
              f"{len(orders['data'])} orders, "
              f"{len(assays['data'])} assays")
        
        # Example 2: Process samples in batches
        if samples['data']:
            sample_ids = [s['id'] for s in samples['data'][:5]]  # First 5 samples
            print(f"Updating status for samples: {sample_ids}")
            
            # Uncomment to actually update
            # await processor.bulk_sample_status_update(sample_ids, "in_progress")
        
    except Exception as e:
        print(f"Error in batch operations: {e}")
    finally:
        qb.close()


def data_analysis_example():
    """Example of data analysis and reporting."""
    
    qb = qbench.connect(
        base_url="https://your-qbench-instance.com",
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    
    processor = QBenchDataProcessor(qb)
    
    try:
        # Generate comprehensive report
        print("Generating sample report...")
        report = processor.generate_sample_report(date_range_days=7)
        
        if report:
            print("\n--- Sample Report ---")
            print(f"Report Date: {report['report_date']}")
            print(f"Date Range: {report['date_range']['days']} days")
            print(f"Total Samples: {report['summary']['total_samples']}")
            
            print("\nStatus Breakdown:")
            for status, count in report['summary']['status_breakdown'].items():
                print(f"  {status}: {count}")
            
            print(f"\nUnique Customers: {len(report['summary']['customer_breakdown'])}")
            print(f"Unique Assays: {len(report['summary']['assay_breakdown'])}")
        
        # Export samples to CSV
        print("\nExporting samples to CSV...")
        processor.export_samples_to_csv(
            'qbench_samples_export.csv',
            filters={'limit': 100, 'status': 'active'}
        )
        
    except Exception as e:
        print(f"Error in data analysis: {e}")
    finally:
        qb.close()


def integration_example():
    """Example of integrating QBench with external systems."""
    
    qb = qbench.connect(
        base_url="https://your-qbench-instance.com",
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    
    try:
        # Example: Sync QBench customers with external CRM
        print("Syncing customer data...")
        
        customers_data = qb.get_customers()
        customers = customers_data.get('data', [])
        
        # Process customers for external system
        external_format = []
        for customer in customers[:10]:  # First 10 customers
            external_customer = {
                'external_id': customer.get('id'),
                'company_name': customer.get('name'),
                'email': customer.get('email'),
                'phone': customer.get('phone'),
                'qbench_data': customer  # Keep original data
            }
            external_format.append(external_customer)
        
        print(f"Prepared {len(external_format)} customers for external sync")
        
        # Here you would typically send this data to your external system
        # external_crm.sync_customers(external_format)
        
        # Example: Monitor sample status changes
        print("\nMonitoring sample statuses...")
        
        # Get samples that might need attention
        pending_samples = qb.get_samples(status='pending')
        in_progress_samples = qb.get_samples(status='in_progress')
        
        print(f"Pending samples: {len(pending_samples['data'])}")
        print(f"In progress samples: {len(in_progress_samples['data'])}")
        
        # Alert if too many pending samples
        if len(pending_samples['data']) > 50:
            print("⚠️  Alert: High number of pending samples!")
            # send_alert_notification(pending_samples['data'])
        
    except Exception as e:
        print(f"Error in integration: {e}")
    finally:
        qb.close()


def custom_endpoint_example():
    """Example of working with specific endpoint configurations."""
    
    qb = qbench.connect(
        base_url="https://your-qbench-instance.com",
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    
    try:
        # List all available endpoints
        endpoints = qb.list_available_endpoints()
        print(f"Available endpoints: {len(endpoints)}")
        
        # Get information about specific endpoints
        sample_endpoint_info = qb.get_endpoint_info('get_samples')
        print(f"Sample endpoint info: {sample_endpoint_info}")
        
        # Work with different endpoint types
        print("\n--- Paginated Endpoints ---")
        paginated_endpoints = [
            name for name in endpoints 
            if qb.get_endpoint_info(name).get('paginated', False)
        ]
        print(f"Paginated endpoints: {len(paginated_endpoints)}")
        for endpoint in paginated_endpoints[:5]:
            print(f"  - {endpoint}")
        
        print("\n--- Non-Paginated Endpoints ---")
        non_paginated = [
            name for name in endpoints 
            if not qb.get_endpoint_info(name).get('paginated', False)
        ]
        print(f"Non-paginated endpoints: {len(non_paginated)}")
        for endpoint in non_paginated[:5]:
            print(f"  - {endpoint}")
        
    except Exception as e:
        print(f"Error exploring endpoints: {e}")
    finally:
        qb.close()


def main():
    """Main advanced examples runner."""
    print("QBench SDK Advanced Examples")
    print("=" * 50)
    
    print("\n--- Batch Operations (Async) ---")
    asyncio.run(batch_operations_example())
    
    print("\n--- Data Analysis ---")
    data_analysis_example()
    
    print("\n--- Integration Example ---")
    integration_example()
    
    print("\n--- Custom Endpoint Example ---")
    custom_endpoint_example()


if __name__ == "__main__":
    main()
