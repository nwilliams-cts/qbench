import qbench

def main():
    qb = qbench.connect(base_url="https://origo.qbench.net", api_key="c94e7029-441a-46a6-aad9-766f0faf30cf", api_secret="692d418c-73af-4c0b-9a5a-78755f426aab")
    filters = {
        "customer_account_id": "73"
    }
    res = qb.get_order_list(page_limit=1, **filters)
    print(res)

if __name__ == "__main__":
    main()