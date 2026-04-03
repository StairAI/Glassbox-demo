"""Quick debug script to test CryptoPanic API directly."""

import requests

# Try different endpoint variations
endpoints = [
    "https://cryptopanic.com/web-api/posts/",
    "https://cryptopanic.com/api/v1/posts/",
    "https://cryptopanic.com/api/free/v1/posts/",
    "https://cryptopanic.com/api/posts/",
]

params = {
    "auth_token": "1faf4af4f599defbd358148d7edbce39c9da3dcb",
    "public": "true"
}

for url in endpoints:
    print("=" * 80)
    print(f"Testing: {url}")
    print(f"Params: {params}")
    print()

    try:
        response = requests.get(url, params=params, timeout=30)
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
                        print(f"First result keys: {list(data['results'][0].keys())}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
            break
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response (first 200 chars): {response.text[:200]}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()
