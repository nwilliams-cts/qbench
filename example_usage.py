import qbench

def main():
    qb = qbench.connect(base_url="https://origo.qbench.net", api_key="0c278123-168f-4611-b1da-99bc95963286", api_secret="545f4438-9b52-4e09-b032-d138c3fb7cac")
    filters = {
        "customer_account_id": "73"
    }
    res = qb.get_order_list(page_limit=1, **filters)
    print(res)

if __name__ == "__main__":
    main()