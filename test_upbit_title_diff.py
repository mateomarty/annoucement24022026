#!/usr/bin/env python3
"""
Test script to compare Upbit notice title formats across different API endpoints.
Goal: find which endpoint returns titles WITHOUT the trailing parenthetical text.

Example:
  WITH parenthesis:    스카이프로토콜(SKY), 유에스디에스(USDS) KRW, USDT 마켓 디지털 자산 추가 (USDS 거래지원 개시 시점 변경 안내)
  WITHOUT parenthesis: 스카이프로토콜(SKY), 유에스디에스(USDS) KRW, USDT 마켓 디지털 자산 추가

Run this on a machine with direct internet access (no proxy blocking upbit.com).
Requires: pip install curl_cffi
"""

from curl_cffi import requests
import json
import sys
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://upbit.com/",
    "Origin": "https://upbit.com",
}

ENDPOINTS = [
    # ============================================================
    # GROUP 1: NOTICES endpoints (probably what you use now)
    # ============================================================
    {
        "name": "notices (default)",
        "url": "https://api-manager.upbit.com/api/v1/notices",
        "params": {"page": 1, "per_page": 20},
    },
    {
        "name": "notices (os=web)",
        "url": "https://api-manager.upbit.com/api/v1/notices",
        "params": {"os": "web", "page": 1, "per_page": 20},
    },
    {
        "name": "notices (thread=general)",
        "url": "https://api-manager.upbit.com/api/v1/notices",
        "params": {"page": 1, "per_page": 20, "thread_name": "general"},
    },
    {
        "name": "notices (thread=listing)",
        "url": "https://api-manager.upbit.com/api/v1/notices",
        "params": {"page": 1, "per_page": 20, "thread_name": "listing"},
    },
    {
        "name": "notices/search",
        "url": "https://api-manager.upbit.com/api/v1/notices/search",
        "params": {"page": 1, "per_page": 20, "search": "디지털 자산 추가"},
    },
    {
        "name": "notices/search (partition=1)",
        "url": "https://api-manager.upbit.com/api/v1/notices/search",
        "params": {"search": "", "page": 1, "per_page": 20, "partition": 1, "target": "non_ios", "thread_name": "general"},
    },

    # ============================================================
    # GROUP 2: ANNOUNCEMENTS endpoints (LIKELY the one without parenthesis!)
    # ============================================================
    {
        "name": "*** announcements (all) ***",
        "url": "https://api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "all"},
    },
    {
        "name": "*** announcements (listing) ***",
        "url": "https://api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "listing"},
    },
    {
        "name": "announcements (no params)",
        "url": "https://api-manager.upbit.com/api/v1/announcements",
        "params": {"page": 1, "per_page": 20},
    },
    {
        "name": "announcements (category=trade)",
        "url": "https://api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "trade"},
    },

    # ============================================================
    # GROUP 3: DISCLOSURE endpoint (project-team subdomain)
    # ============================================================
    {
        "name": "disclosure (kr)",
        "url": "https://project-team.upbit.com/api/v1/disclosure",
        "params": {"region": "kr", "per_page": 20},
    },
    {
        "name": "disclosure (default)",
        "url": "https://project-team.upbit.com/api/v1/disclosure",
        "params": {"per_page": 20},
    },

    # ============================================================
    # GROUP 4: SINGAPORE / international variants
    # ============================================================
    {
        "name": "sg-announcements",
        "url": "https://sg-api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "all"},
    },
    {
        "name": "id-announcements",
        "url": "https://id-api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "all"},
    },
    {
        "name": "th-announcements",
        "url": "https://th-api-manager.upbit.com/api/v1/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "all"},
    },

    # ============================================================
    # GROUP 5: Specific notice ID 6102 (direct fetch)
    # ============================================================
    {
        "name": "notice/6102 direct",
        "url": "https://api-manager.upbit.com/api/v1/notices/6102",
        "params": {},
    },
    {
        "name": "announcement/6102 direct",
        "url": "https://api-manager.upbit.com/api/v1/announcements/6102",
        "params": {},
    },

    # ============================================================
    # GROUP 6: V2 variants
    # ============================================================
    {
        "name": "v2/notices",
        "url": "https://api-manager.upbit.com/api/v2/notices",
        "params": {"page": 1, "per_page": 20},
    },
    {
        "name": "v2/announcements",
        "url": "https://api-manager.upbit.com/api/v2/announcements",
        "params": {"os": "web", "page": 1, "per_page": 20, "category": "all"},
    },

    # ============================================================
    # GROUP 7: Other speculative endpoints
    # ============================================================
    {
        "name": "news",
        "url": "https://api-manager.upbit.com/api/v1/news",
        "params": {"page": 1, "per_page": 20},
    },
    {
        "name": "boards",
        "url": "https://api-manager.upbit.com/api/v1/boards",
        "params": {"page": 1, "per_page": 20},
    },
    {
        "name": "notice_threads",
        "url": "https://api-manager.upbit.com/api/v1/notice_threads",
        "params": {},
    },
    {
        "name": "notices/categories",
        "url": "https://api-manager.upbit.com/api/v1/notices/categories",
        "params": {},
    },
]


def extract_items(data):
    """Try to extract list items from various response structures."""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Try common nesting patterns
        for key in ['data', 'result', 'response']:
            if key in data:
                sub = data[key]
                if isinstance(sub, list):
                    return sub
                if isinstance(sub, dict):
                    for subkey in ['list', 'posts', 'notices', 'announcements', 'items', 'contents']:
                        if subkey in sub and isinstance(sub[subkey], list):
                            return sub[subkey]

        # Direct list keys
        for key in ['list', 'posts', 'notices', 'announcements', 'items', 'contents']:
            if key in data and isinstance(data[key], list):
                return data[key]

    return None


def extract_title(item):
    """Try to get title from various field names."""
    for key in ['title', 'text', 'name', 'subject', 'heading']:
        if key in item:
            return item[key]
    return None


def test_endpoint(ep):
    """Test a single endpoint and return results."""
    name = ep["name"]
    url = ep["url"]
    params = ep["params"]

    try:
        resp = requests.get(
            url,
            params=params,
            headers=HEADERS,
            impersonate="chrome120",
            timeout=10,
        )
        status = resp.status_code

        result = {
            "name": name,
            "url": resp.url,
            "status": status,
            "titles": [],
            "keys": [],
            "raw_snippet": "",
            "error": None,
        }

        if status == 200:
            try:
                data = resp.json()
                items = extract_items(data)

                if items and len(items) > 0:
                    for item in items[:5]:
                        title = extract_title(item)
                        item_id = item.get("id", item.get("noticeId", item.get("notice_id", "?")))
                        if title:
                            result["titles"].append({"id": item_id, "title": title})
                    result["keys"] = list(items[0].keys()) if items else []
                else:
                    # Single item response (e.g., notice by ID)
                    title = extract_title(data) or extract_title(data.get("data", {})) if isinstance(data, dict) else None
                    if title:
                        result["titles"].append({"id": "single", "title": title})
                        result["keys"] = list(data.keys()) if isinstance(data, dict) else []
                    else:
                        result["raw_snippet"] = json.dumps(data, ensure_ascii=False)[:500]
                        result["keys"] = list(data.keys()) if isinstance(data, dict) else []
            except Exception as e:
                result["raw_snippet"] = resp.text[:300]
                result["error"] = f"JSON parse error: {e}"
        else:
            result["raw_snippet"] = resp.text[:200]

        return result

    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": -1,
            "titles": [],
            "keys": [],
            "raw_snippet": "",
            "error": str(e),
        }


def main():
    print("=" * 120)
    print("UPBIT ENDPOINT TITLE COMPARISON TEST")
    print("Looking for: title WITHOUT trailing parenthetical")
    print("=" * 120)

    results = []

    for ep in ENDPOINTS:
        result = test_endpoint(ep)
        results.append(result)
        time.sleep(0.2)

    # Print results grouped
    print("\n" + "=" * 120)
    print("RESULTS SUMMARY")
    print("=" * 120)

    for r in results:
        status_icon = "✅" if r["status"] == 200 else "❌" if r["status"] == -1 else f"⚠️ {r['status']}"
        print(f"\n{'─'*100}")
        print(f"{status_icon}  [{r['name']}]")
        print(f"    URL: {r['url']}")

        if r["error"]:
            print(f"    ERROR: {r['error']}")
            continue

        if r["titles"]:
            print(f"    Keys: {r['keys']}")
            for t in r["titles"]:
                title = t["title"]
                # Highlight if title ends with a parenthetical
                has_trailing_paren = title.rstrip().endswith(")")
                marker = "  ← HAS TRAILING PARENTHESIS" if has_trailing_paren else "  ← NO TRAILING PARENTHESIS ★★★"
                print(f"    [{t['id']}] {title}{marker}")
        elif r["raw_snippet"]:
            print(f"    Keys: {r['keys']}")
            print(f"    Raw: {r['raw_snippet'][:200]}")

    # Final analysis
    print("\n" + "=" * 120)
    print("ANALYSIS: Endpoints WITHOUT trailing parenthesis in titles")
    print("=" * 120)
    for r in results:
        if r["titles"]:
            no_paren_titles = [t for t in r["titles"] if not t["title"].rstrip().endswith(")")]
            if no_paren_titles:
                print(f"\n  ★ [{r['name']}] has titles WITHOUT trailing parenthesis:")
                for t in no_paren_titles:
                    print(f"      [{t['id']}] {t['title']}")


if __name__ == "__main__":
    main()
