"""
This file contains a JSON object representing all current endpoints for QBench.
The list is based on the v2 API as of 3/1/2025. Each key in the JSON object is a
valid method to use with the QBenchAPI object. For example, calling:
qb.get_customers() will implicitly call <hostname>/qbench/api/v2/customers a auto-
matically paginate through all customers in the system unless kwargs are added as 
search filters (e.g. qb.get_samples(order_ids=1089)). Some v1 methods are included,
but should be used carefully as their structure can change from instance to instance
and they do not have the same output structure as v2. These may be included at a later 
date if needed, but all work should be attempted in v2 first. Some data however is less
accessible in v2 unless you make multiple API calls.
"""

QBENCH_ENDPOINTS = {
    # ACCESSIONING_TYPE
    "get_accessioning_type": {"method": "GET", "v2": "accessioning-types/{id}", "v1": None},
    "get_accessioning_types": {"method": "GET", "v2": "accessioning-types", "v1": None, "paginated": True},
    
    # API_CLIENT
    "get_api_client": {"method": "GET", "v2": "api-clients/{id}", "v1": None},
    "get_api_clients": {"method": "GET", "v2": "api-clients", "v1": None, "paginated": True},

    # ASSAY
    "create_assays": {"method": "POST", "v2": "assays", "v1": None},

    "get_assay": {"method": "GET", "v2": "assays/{id}", "v1": "assay/{id}"},
    "get_assays": {"method": "GET", "v2": "assays", "v1": "assay", "paginated": True},

    "get_assay_divisions": {"method": "GET", "v2": "assays/{id}/divisions", "v1": None, "paginated": True},
    "get_assay_panels": {"method": "GET", "v2": "assays/{id}/panels", "v1": None, "paginated": True},
    "get_assay_turnarounds": {"method": "GET", "v2": "assays/{id}/turnarounds", "v1": None, "paginated": True},
    "get_assay_attachments": {"method": "GET", "v2": "assays/{id}/attachments", "v1": None, "paginated": True},
    "get_assay_accessioning_types": {"method": "GET", "v2": "assays/{id}/accessioning-types", "v1": None, "paginated": True},

    "update_assays": {"method": "PATCH", "v2": "assays", "v1": None},

    "delete_assay": {"method": "DELETE", "v2": "assays/{id}", "v1": None},

    # ASSAY_CATEGORY
    "get_assay_category": {"method": "GET", "v2": "assay-categories/{id}", "v1": None},
    "get_assay_categories": {"method": "GET", "v2": "assay-categories", "v1": None, "paginated": True},

    # ATTACHMENT
    "create_attachments": {"method": "POST", "v2": "attachments", "v1": None},

    "get_attachment": {"method": "GET", "v2": "attachments/{id}", "v1": None},

    "update_attachments": {"method": "PATCH", "v2": "attachments", "v1": None},

    "delete_attachment": {"method": "DELETE", "v2": "attachments/{id}", "v1": None},

    # AUTHENTICATION
    "get_access_token": {"method": "POST", "v2": "auth/token", "v1": None},
    "refresh_access_token": {"method": "POST", "v2": "auth/token/refresh", "v1": None},
    "get_access_token_info": {"method": "GET", "v2": "auth/token/info", "v1": None},

    # BATCH
    "get_batch": {"method": "GET", "v2": "batches/{id}", "v1": "assay/{id}"},
    "get_batches": {"method": "GET", "v2": "batches", "v1": "assay", "paginated": True},

    "get_batch_children": {"method": "GET", "v2": "batches/{id}/children", "v1": None, "paginated": True},
    "get_batch_parents": {"method": "GET", "v2": "batches/{id}/parents", "v1": None, "paginated": True},
    "get_batch_samples": {"method": "GET", "v2": "batches/{id}/samples", "v1": None, "paginated": True},
    "get_batch_tests": {"method": "GET", "v2": "batches/{id}/tests", "v1": None, "paginated": True},
    "get_batch_attachments": {"method": "GET", "v2": "batches/{id}/attachments", "v1": None, "paginated": True},
    "get_batch_worksheet_data": {"method": "GET", "v2": "batches/{id}/worksheet/data", "v1": None},
     
    # CONTACT
    "create_contacts": {"method": "POST", "v2": "contacts", "v1": None},

    "get_contact": {"method": "GET", "v2": "contacts/{id}", "v1": "contact/{id}"},
    "get_contacts": {"method": "GET", "v2": "contacts", "v1": "contact", "paginated": True},

    "get_contact_customers": {"method": "GET", "v2": "contacts/{id}/customers", "v1": None, "paginated": True},

    "update_contacts": {"method": "PATCH", "v2": "contacts", "v1": None},

    "delete_contact": {"method": "DELETE", "v2": "contacts/{id}", "v1": None},
    # CUSTOMER
    "create_customers": {"method": "POST", "v2": "customers", "v1": None},

    "get_customer": {"method": "GET", "v2": "customers/{id}", "v1": "customer/{id}"},
    "get_customers": {"method": "GET", "v2": "customers", "v1": "customer", "paginated": True},
    "get_customer_contacts": {"method": "GET", "v2": "customers/{id}/contacts", "v1": None, "paginated": True},
    "get_customer_divisions": {"method": "GET", "v2": "customers/{id}/divisions", "v1": None, "paginated": True},
    "get_customer_sources": {"method": "GET", "v2": "customers/{id}/sources", "v1": None, "paginated": True},
    "get_customer_attachments": {"method": "GET", "v2": "customers/{id}/attachments", "v1": None, "paginated": True},
    "get_customer_api_clients": {"method": "GET", "v2": "customers/{id}/api-clients", "v1": None, "paginated": True},
    "update_customers": {"method": "PATCH", "v2": "customers", "v1": None},

    "delete_customer": {"method": "DELETE", "v2": "customers/{id}", "v1": None},

    # DIVISION
    "get_division": {"method": "GET", "v2": "divisions/{id}", "v1": "division/{id}"},
    "get_divisions": {"method": "GET", "v2": "divisions", "v1": "division", "paginated": True},
    
    # EPIC
    "get_epic": {"method": "GET", "v2": "epics/{id}", "v1": "epic/{id}"},
    "get_epics": {"method": "GET", "v2": "epics", "v1": "epic", "paginated": True},

    # INVOICE
    "create_invoices": {"method": "POST", "v2": "invoices", "v1": None},

    "get_invoice": {"method": "GET", "v2": "invoices/{id}", "v1": "invoice/{id}"},
    "get_invoices": {"method": "GET", "v2": "invoices", "v1": "invoice", "paginated": True},
    "get_invoice_orders": {"method": "GET", "v2": "invoices/{id}/orders", "v1": None, "paginated": True},
    "get_invoice_payments": {"method": "GET", "v2": "invoices/{id}/payments", "v1": None, "paginated": True},
    "get_invoice_invoice_items": {"method": "GET", "v2": "invoices/{id}/invoice-items", "v1": None, "paginated": True},

    "sync_invoice": {"method": "POST", "v2": "invoices/{id}/sync", "v1": None},

    "update_invoices": {"method": "PATCH", "v2": "invoices", "v1": None},

    "delete_invoice": {"method": "DELETE", "v2": "invoices/{id}", "v1": None},

    # INVOICE_ITEM
    "create_invoice_items": {"method": "POST", "v2": "invoice-items", "v1": None},

    "get_invoice_item": {"method": "GET", "v2": "invoice-items/{id}", "v1": "invoice-item/{id}"},
    "get_invoice_items": {"method": "GET", "v2": "invoice-items", "v1": "invoice-item", "paginated": True},

    "update_invoice_items": {"method": "PATCH", "v2": "invoice-items", "v1": None},

    "delete_invoice_item": {"method": "DELETE", "v2": "invoice-items/{id}", "v1": None},

    # KVSTORE
    "get_kvstore": {"method": "GET", "v2": "kvstores/{id}", "v1": None},

    # LABEL
    "print_order_labels": {"method": "POST", "v2": "labels/{id}/orders", "v1": None},
    "print_sample_labels": {"method": "POST", "v2": "labels/{id}/samples", "v1": None},
    "print_test_labels": {"method": "POST", "v2": "labels/{id}/tests", "v1": None},
    "print_batch_labels": {"method": "POST", "v2": "labels/{id}/batches", "v1": None},
    "print_project_labels": {"method": "POST", "v2": "labels/{id}/projects", "v1": None},
    "print_location_labels": {"method": "POST", "v2": "labels/{id}/locations", "v1": None},

    # LOCATION
    "get_location": {"method": "GET", "v2": "locations/{id}", "v1": "location/{id}"},
    "get_locations": {"method": "GET", "v2": "locations", "v1": "location", "paginated": True},

    # LOCATION_TYPE
    "get_location_type": {"method": "GET", "v2": "location-types/{id}", "v1": "location-type/{id}"},
    "get_location_types": {"method": "GET", "v2": "location-types", "v1": "location-type", "paginated": True},

    # ORDER
    "create_orders": {"method": "POST", "v2": "orders", "v1": None},

    "get_order": {"method": "GET", "v2": "orders/{id}", "v1": "order/{id}"},
    "get_orders": {"method": "GET", "v2": "orders", "v1": "order", "paginated": True},
    "get_order_invoices": {"method": "GET", "v2": "orders/{id}/invoices", "v1": None, "paginated": True},
    "get_order_reports": {"method": "GET", "v2": "orders/{id}/reports", "v1": None, "paginated": True},
    "get_order_samples": {"method": "GET", "v2": "orders/{id}/samples", "v1": None, "paginated": True},
    "get_order_tests": {"method": "GET", "v2": "orders/{id}/tests", "v1": None, "paginated": True},
    "get_order_attachments": {"method": "GET", "v2": "orders/{id}/attachments", "v1": None, "paginated": True},

    "update_orders": {"method": "PATCH", "v2": "orders", "v1": None},

    "delete_order": {"method": "DELETE", "v2": "orders/{id}", "v1": None},

    # PANEL
    "create_panels": {"method": "POST", "v2": "panels", "v1": None},

    "get_panel": {"method": "GET", "v2": "panels/{id}", "v1": "panel/{id}"},
    "get_panels": {"method": "GET", "v2": "panels", "v1": "panel", "paginated": True},
    "get_panel_assays": {"method": "GET", "v2": "panels/{id}/assays", "v1": None, "paginated": True},

    "update_panels": {"method": "PATCH", "v2": "panels", "v1": None},

    "delete_panel": {"method": "DELETE", "v2": "panels/{id}", "v1": None},

    # PAYMENT
    "create_payments": {"method": "POST", "v2": "payments", "v1": None},
    "apply_payment_to_invoice": {"method": "POST", "v2": "payments/{id}/invoices", "v1": None},
    "send_payment_email": {"method": "POST", "v2": "payments/{id}/send-email", "v1": None},

    "get_payment": {"method": "GET", "v2": "payments/{id}", "v1": "payment/{id}"},
    "get_payments": {"method": "GET", "v2": "payments", "v1": "payment", "paginated": True},
    "get_payment_invoices": {"method": "GET", "v2": "payments/{id}/invoices", "v1": None, "paginated": True},

    "update_payments": {"method": "PATCH", "v2": "payments", "v1": None},

    "delete_payment": {"method": "DELETE", "v2": "payments/{id}", "v1": None},
    # "unapply_payment": {"method": "DELETE", "v2": "payments/{id}/invoices/{id2}", "v1": None}

    # PRINTDOC
    "create_printdocs": {"method": "POST", "v2": "printdocs", "v1": None},

    "get_printdoc": {"method": "GET", "v2": "printdocs/{id}", "v1": None},

    # PROJECT
    "get_project": {"method": "GET", "v2": "projects/{id}", "v1": "project/{id}"},
    "get_projects": {"method": "GET", "v2": "projects", "v1": "project", "paginated": True},

    # REPORT
    "create_reports": {"method": "POST", "v2": "reports", "v1": None},
    # There is a publish report endpoint, but it's not clear how it works in the docs. Only order reports seem supported.

    "get_report": {"method": "GET", "v2": "reports/{id}", "v1": None},
    "get_reports": {"method": "GET", "v2": "reports", "v1": None, "paginated": True},

    # SAMPLE
    "create_samples": {"method": "POST", "v2": "samples", "v1": None},

    "get_sample": {"method": "GET", "v2": "samples/{id}", "v1": "sample/{id}"},
    "get_samples": {"method": "GET", "v2": "samples", "v1": "sample", "paginated": True},
    "get_sample_batches": {"method": "GET", "v2": "samples/{id}/batches", "v1": None, "paginated": True},
    "get_sample_reports": {"method": "GET", "v2": "samples/{id}/reports", "v1": None, "paginated": True},
    "get_sample_subsamples": {"method": "GET", "v2": "samples/{id}/sub-samples", "v1": None, "paginated": True},
    "get_sample_tests": {"method": "GET", "v2": "samples/{id}/tests", "v1": None, "paginated": True},
    "get_sample_attachments": {"method": "GET", "v2": "samples/{id}/attachments", "v1": None, "paginated": True},

    "update_samples": {"method": "PATCH", "v2": "samples", "v1": None},

    "delete_sample": {"method": "DELETE", "v2": "samples/{id}", "v1": None},

    # SOURCE
    "get_source": {"method": "GET", "v2": "sources/{id}", "v1": None},
    "get_sources": {"method": "GET", "v2": "sources", "v1": None, "paginated": True},

    # TEAM
    "get_team": {"method": "GET", "v2": "teams/{id}", "v1": None},
    "get_teams": {"method": "GET", "v2": "teams", "v1": None, "paginated": True},

    # TEST
    "create_tests": {"method": "POST", "v2": "tests", "v1": None},

    "get_test": {"method": "GET", "v2": "tests/{id}", "v1": "test/{id}"},
    "get_tests": {"method": "GET", "v2": "tests", "v1": "test", "paginated": True},
    "get_test_batches": {"method": "GET", "v2": "tests/{id}/batches", "v1": None, "paginated": True},
    "get_test_reports": {"method": "GET", "v2": "tests/{id}/reports", "v1": None, "paginated": True},
    "get_test_attachments": {"method": "GET", "v2": "tests/{id}/attachments", "v1": None, "paginated": True},
    "get_test_worksheet_data": {"method": "GET", "v2": "tests/{id}/worksheet/data", "v1": None},

    "update_tests": {"method": "PATCH", "v2": "tests", "v1": None},

    "delete_test": {"method": "DELETE", "v2": "tests/{id}", "v1": None},

    # TURNAROUND
    "create_turnarounds": {"method": "POST", "v2": "turnarounds", "v1": None},

    "get_turnaround": {"method": "GET", "v2": "turnarounds/{id}", "v1": None},
    "get_turnarounds": {"method": "GET", "v2": "turnarounds", "v1": None, "paginated": True},
    "get_turnaround_divisions": {"method": "GET", "v2": "turnarounds/{id}/divisions", "v1": None, "paginated": True},

    "update_turnarounds": {"method": "PATCH", "v2": "turnarounds", "v1": None},

    "delete_turnaround": {"method": "DELETE", "v2": "turnarounds/{id}", "v1": None},

    # USER
    "get_user": {"method": "GET", "v2": "users/{id}", "v1": None},
    "get_users": {"method": "GET", "v2": "users", "v1": None, "paginated": True},

    # WORKSHEET
    "get_worksheet": {"method": "GET", "v2": "worksheets/{id}", "v1": None},
    "get_worksheets": {"method": "GET", "v2": "worksheets", "v1": None, "paginated": True},
}
