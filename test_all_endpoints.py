#!/usr/bin/env python3
"""Test all known Upbit notice/announcement endpoints to compare title formats."""

from curl_cffi import requests
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://upbit.com/",
    "Origin": "https://upbit.com",
}

endpoints = [
    # Notices endpoints (what you're probably using)
    ("notices (default)", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20"),
    ("notices (general)", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20&thread_name=general"),
    ("notices (listing)", "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20&thread_name=listing"),
    ("notices (os=web)", "https://api-manager.upbit.com/api/v1/notices?os=web&page=1&per_page=20"),
    ("notices search", "https://api-manager.upbit.com/api/v1/notices/search?page=1&per_page=20"),

    # Announcements endpoints (different from notices!)
    ("announcements (all)", "https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=all"),
    ("announcements (listing)", "https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=listing"),
    ("announcements (default)", "https://api-manager.upbit.com/api/v1/announcements?page=1&per_page=20"),

    # Disclosure endpoint
    ("disclosure (kr)", "https://project-team.upbit.com/api/v1/disclosure?region=kr&per_page=20"),
    ("disclosure (default)", "https://project-team.upbit.com/api/v1/disclosure?per_page=20"),

    # Singapore variants
    ("sg announcements", "https://sg-api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=all"),
    ("sg notices", "https://sg-api-manager.upbit.com/api/v1/notices?page=1&per_page=20"),

    # V2 variants
    ("v2 notices", "https://api-manager.upbit.com/api/v2/notices?page=1&per_page=20"),
    ("v2 announcements", "https://api-manager.upbit.com/api/v2/announcements?os=web&page=1&per_page=20"),

    # Other possible endpoints
    ("notice threads", "https://api-manager.upbit.com/api/v1/notice_threads"),
    ("categories", "https://api-manager.upbit.com/api/v1/notices/categories"),
    ("market notice", "https://api-manager.upbit.com/api/v1/market/notices?page=1&per_page=20"),
    ("news", "https://api-manager.upbit.com/api/v1/news?page=1&per_page=20"),

    # Specific notice by ID 6102
    ("notice 6102", "https://api-manager.upbit.com/api/v1/notices/6102"),
    ("announcement 6102", "https://api-manager.upbit.com/api/v1/announcements/6102"),
]

print("=" * 120)
print("TESTING ALL UPBIT ENDPOINTS - Looking for title format differences")
print("=" * 120)

for name, url in endpoints:
    try:
        resp = requests.get(url, headers=HEADERS, impersonate="chrome120", timeout=10)
        status = resp.status_code
        content_type = resp.headers.get("Content-Type", "unknown")

        print(f"\n{'='*100}")
        print(f"[{name}] Status: {status}")
        print(f"URL: {url}")

        if status == 200:
            try:
                data = resp.json()
                # Try to find titles in the response
                raw = json.dumps(data, ensure_ascii=False, indent=2)

                # Look for title fields
                if isinstance(data, dict):
                    # Check common structures
                    items = None
                    if 'data' in data and isinstance(data['data'], dict):
                        if 'list' in data['data']:
                            items = data['data']['list']
                        elif 'posts' in data['data']:
                            items = data['data']['posts']
                        elif 'notices' in data['data']:
                            items = data['data']['notices']
                    elif 'data' in data and isinstance(data['data'], list):
                        items = data['data']
                    elif 'list' in data:
                        items = data['list']
                    elif 'notices' in data:
                        items = data['notices']

                    if items and isinstance(items, list):
                        print(f"Found {len(items)} items. First 3 titles:")
                        for i, item in enumerate(items[:3]):
                            title = item.get('title', item.get('text', item.get('name', 'NO_TITLE_FIELD')))
                            item_id = item.get('id', item.get('noticeId', 'NO_ID'))
                            print(f"  [{item_id}] {title}")
                            # Print all keys for first item
                            if i == 0:
                                print(f"  Keys: {list(item.keys())}")
                    else:
                        # Just dump truncated
                        print(f"Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        print(raw[:800])
                else:
                    print(raw[:800])
            except Exception as e:
                print(f"Parse error: {e}")
                print(resp.text[:500])
        else:
            print(f"Response: {resp.text[:300]}")

    except Exception as e:
        print(f"\n[{name}] URL: {url}")
        print(f"ERROR: {e}")

    time.sleep(0.3)
