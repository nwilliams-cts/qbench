import qbench

def main():
    qb = qbench.connect(base_url="https://<my-lims>.qbench.net", api_key="<API-KEY>", api_secret="<API-SECRET>")
    filters = {
        "customer_account_id": "1"
    }
    res = qb.get_order_list(page_limit=1, **filters)
    print(res)

if __name__ == "__main__":
    main()