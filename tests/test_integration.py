"""Integration tests for QBench SDK."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from qbench import connect
from qbench.exceptions import QBenchAPIError


class TestQBenchIntegration:
    """Integration test cases for QBench SDK."""
    
    def test_full_sync_workflow(self):
        """Test a complete synchronous workflow."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            with patch('requests.Session.request') as mock_request:
                # Mock successful responses
                sample_response = Mock()
                sample_response.status_code = 200
                sample_response.json.return_value = {
                    "data": [{"id": 1, "name": "Test Sample"}],
                    "total_pages": 1
                }
                sample_response.raise_for_status.return_value = None
                
                customer_response = Mock()
                customer_response.status_code = 200
                customer_response.json.return_value = {"id": 123, "name": "ACME Corp"}
                customer_response.raise_for_status.return_value = None
                
                # Set up different responses for different endpoints
                def mock_request_side_effect(method, url, **kwargs):
                    if 'samples' in url:
                        return sample_response
                    elif 'customers' in url:
                        return customer_response
                    return sample_response
                
                mock_request.side_effect = mock_request_side_effect
                
                # Create client and test workflow
                qb = connect(
                    base_url="https://test.qbench.com",
                    api_key="test_key",
                    api_secret="test_secret"
                )
                
                # Test health check
                health = qb.health_check()
                assert health['status'] == 'healthy'
                
                # Test getting samples (paginated)
                with patch.object(qb, '_get_entity_list') as mock_paginated:
                    mock_paginated.return_value = {"data": [{"id": 1, "name": "Test Sample"}]}
                    samples = qb.get_samples()
                    assert len(samples['data']) == 1
                
                # Test getting single customer
                customer = qb.get_customer(entity_id=123)
                assert customer['id'] == 123
                
                # Test endpoint info
                info = qb.get_endpoint_info('get_samples')
                assert info['name'] == 'get_samples'
                
                # Clean up
                qb.close()
    
    @pytest.mark.asyncio
    async def test_full_async_workflow(self):
        """Test a complete asynchronous workflow."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            with patch('requests.Session.request'):
                qb = connect(
                    base_url="https://test.qbench.com",
                    api_key="test_key",
                    api_secret="test_secret"
                )
                
                # Mock async pagination
                with patch.object(qb, '_get_entity_list') as mock_paginated:
                    mock_paginated.return_value = {
                        "data": [
                            {"id": 1, "name": "Sample 1"},
                            {"id": 2, "name": "Sample 2"}
                        ]
                    }
                    
                    # Test async calls
                    samples = await qb.get_samples()
                    customers = await qb.get_customers()
                    
                    assert len(samples['data']) == 2
                    assert len(customers['data']) == 2
                
                qb.close()
    
    def test_error_propagation(self):
        """Test that errors are properly propagated through the stack."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            qb = connect(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret"
            )
            
            # Test invalid endpoint
            with pytest.raises(AttributeError) as exc_info:
                qb.invalid_endpoint()
            
            assert "invalid_endpoint" in str(exc_info.value)
            
            # Test invalid endpoint info
            with pytest.raises(Exception):  # QBenchValidationError
                qb.get_endpoint_info('invalid_endpoint')
            
            qb.close()
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            qb = connect(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret",
                concurrency_limit=5  # Test custom concurrency limit
            )
            
            assert qb._concurrency_limit == 5
            
            # Test that multiple health checks work
            with patch.object(qb, '_make_request') as mock_request:
                mock_request.return_value = {"data": []}
                
                results = []
                for _ in range(3):
                    results.append(qb.health_check())
                
                # All should succeed
                assert all(r['status'] == 'healthy' for r in results)
                assert mock_request.call_count == 3
            
            qb.close()
    
    def test_different_api_versions(self):
        """Test switching between API versions."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            qb = connect(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret"
            )
            
            with patch.object(qb, '_make_request') as mock_request:
                mock_request.return_value = {"id": 1, "name": "Test"}
                
                # Test v2 (default)
                result_v2 = qb.get_sample(entity_id=1, use_v1=False)
                
                # Test v1
                result_v1 = qb.get_sample(entity_id=1, use_v1=True)
                
                # Both should work
                assert result_v2['id'] == 1
                assert result_v1['id'] == 1
                
                # Check that use_v1 parameter was passed correctly
                calls = mock_request.call_args_list
                assert len(calls) == 2
                
                # First call should be v2 (use_v1=False)
                assert calls[0][0][2] is False
                # Second call should be v1 (use_v1=True)
                assert calls[1][0][2] is True
            
            qb.close()
    
    def test_data_creation_workflow(self):
        """Test data creation and modification workflow."""
        with patch('qbench.auth.QBenchAuth._fetch_access_token'):
            qb = connect(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret"
            )
            
            with patch.object(qb, '_make_request') as mock_request:
                # Mock creation response
                mock_request.return_value = {"id": 123, "name": "New Customer", "status": "created"}
                
                # Test creating customer
                new_customer_data = {
                    "name": "ACME Corporation",
                    "email": "contact@acme.com"
                }
                
                result = qb.create_customers(data=new_customer_data)
                
                assert result['id'] == 123
                assert result['status'] == 'created'
                
                # Verify the data was passed correctly
                call_args = mock_request.call_args
                assert call_args[0][4] == new_customer_data  # data parameter
                assert call_args[0][0] == 'POST'  # method
                
            qb.close()


if __name__ == '__main__':
    pytest.main([__file__])
