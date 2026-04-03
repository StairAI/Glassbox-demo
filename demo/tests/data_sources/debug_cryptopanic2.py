"""Test CryptoPanic with different HTTP methods and headers."""

import requests
import json

# Test endpoint
url = "https://cryptopanic.com/web-api/posts/"

# Test with different methods and headers
configs = [
    {
        "name": "GET with query params",
        "method": "GET",
        "params": {"auth_token": "1faf4af4f599defbd358148d7edbce39c9da3dcb", "public": "true"},
        "headers": {}
    },
    {
        "name": "POST with query params",
        "method": "POST",
        "params": {"auth_token": "1faf4af4f599defbd358148d7edbce39c9da3dcb", "public": "true"},
        "headers": {}
    },
    {
        "name": "POST with JSON body",
        "method": "POST",
        "params": {},
        "headers": {"Content-Type": "application/json"},
        "json": {"auth_token": "1faf4af4f599defbd358148d7edbce39c9da3dcb", "public": True}
    },
    {
        "name": "GET with Authorization header",
        "method": "GET",
        "params": {},
        "headers": {"Authorization": "Bearer 1faf4af4f599defbd358148d7edbce39c9da3dcb"}
    },
]

for config in configs:
    print("=" * 80)
    print(f"Testing: {config['name']}")
    print(f"Method: {config['method']}")
    print()

    try:
        if config['method'] == 'GET':
            response = requests.get(
                url,
                params=config['params'],
                headers=config['headers'],
                timeout=30
            )
        else:
            json_body = config.get('json')
            if json_body:
                response = requests.post(
                    url,
                    json=json_body,
                    headers=config['headers'],
                    timeout=30
                )
            else:
                response = requests.post(
                    url,
                    params=config['params'],
                    headers=config['headers'],
                    timeout=30
                )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ SUCCESS!")
            try:
                data = response.json()
                print(f"JSON Keys: {list(data.keys())}")
                if "results" in data:
                    print(f"Number of results: {len(data['results'])}")
                    if data['results']:
                        print(f"First result title: {data['results'][0].get('title', 'N/A')}")
            except Exception as e:
                print(f"Response text (first 200 chars): {response.text[:200]}")
            break
        else:
            print(f"✗ Failed")
            print(f"Response (first 200 chars): {response.text[:200]}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()
