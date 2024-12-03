import qbench

def main():
    qb = qbench.connect(base_url="<yourdomainhere>", api_key="<yourapikeyhere>", api_secret="<yourapisecrethere>")
    filters = {
        "customer_account_id": "73"
    }
    res = qb.get_order_list(page_limit=1, **filters)
    print(res)

if __name__ == "__main__":
    main()