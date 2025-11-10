import httpx

services = {
    "LOYALTY_URL": "http://loyalty:8050",
    "PAYMENT_URL": "http://payment:8060",
    "RESERVATION_URL": "http://reservation:8070",
}

client = httpx.Client(timeout=5.0)

def check_health():
    results = {}
    for name, base_url in services.items():
        try:
            r = client.get(f"{base_url}/manage/health")
            results[name] = {"status_code": r.status_code, "body": r.json()}
        except Exception as e:
            results[name] = {"error": str(e)}
    return results
