import requests
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://upbit.com/",
    "Origin": "https://upbit.com",
}

# List of known/suspected Upbit API endpoints for notices
endpoints = [
    # Standard notice API
    ("api-manager notices", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=5"),
    ("api-manager notices general", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=5&thread_name=general"),
    ("api-manager notices listing", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=5&thread_name=listing"),

    # Possible alternative API paths
    ("api-manager v2 notices", "https://api-manager.upbit.com/api/v2/notices?page=1&per_page=5"),
    ("api-manager announcements", "https://api-manager.upbit.com/api/v1/announcements?page=1&per_page=5"),

    # Direct upbit API
    ("upbit api notices", "https://upbit.com/api/v1/notices?page=1&per_page=5"),

    # Possible SSE/websocket-like endpoints
    ("api-manager notice categories", "https://api-manager.upbit.com/api/v1/notices/categories"),

    # Community/board endpoints
    ("api-manager boards", "https://api-manager.upbit.com/api/v1/boards?page=1&per_page=5"),

    # Specific notice by ID
    ("api-manager notice 6102", "https://api-manager.upbit.com/api/v1/notices/6102"),

    # Project/coin listing endpoints
    ("api-manager projects", "https://api-manager.upbit.com/api/v1/projects"),
    ("api-manager market events", "https://api-manager.upbit.com/api/v1/market_events"),

    # RSS feed
    ("upbit rss", "https://upbit.com/rss"),

    # Other possible paths
    ("api-manager service_center", "https://api-manager.upbit.com/api/v1/service_center/notices?page=1&per_page=5"),
    ("api-manager notice threads", "https://api-manager.upbit.com/api/v1/notice_threads"),

    # Trending/popular
    ("api-manager trending", "https://api-manager.upbit.com/api/v1/notices/trending"),

    # Disclosure endpoints
    ("api-manager disclosure", "https://api-manager.upbit.com/api/v1/disclosure?page=1&per_page=5"),

    # Possible CDN/static endpoints
    ("static notices", "https://static.upbit.com/notices.json"),

    # Exchange API (different subdomain patterns)
    ("api upbit notices", "https://api.upbit.com/v1/notices?page=1&per_page=5"),
    ("crix notices", "https://crix-api-endpoint.upbit.com/v1/notices"),

    # Sitemap for discovery
    ("sitemap", "https://upbit.com/sitemap.xml"),
]

print("=" * 100)
print("TESTING UPBIT ENDPOINTS")
print("=" * 100)

for name, url in endpoints:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        status = resp.status_code
        content_type = resp.headers.get("Content-Type", "unknown")
        body = resp.text[:2000]

        print(f"\n{'='*80}")
        print(f"[{name}] {url}")
        print(f"Status: {status} | Content-Type: {content_type}")

        if status == 200:
            # Try to parse as JSON
            try:
                data = resp.json()
                print(f"JSON Response (truncated):")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])
            except:
                print(f"Raw Response (truncated):")
                print(body[:1000])
        else:
            print(f"Response: {body[:300]}")

    except Exception as e:
        print(f"\n[{name}] {url}")
        print(f"ERROR: {e}")

    time.sleep(0.3)
