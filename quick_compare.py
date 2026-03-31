#!/usr/bin/env python3
"""
Quick side-by-side comparison of /notices vs /announcements title formats.
Run this on a machine with direct access to upbit.com.

pip install curl_cffi
"""

from curl_cffi import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://upbit.com/",
    "Origin": "https://upbit.com",
}


def fetch(url, params):
    resp = requests.get(url, params=params, headers=HEADERS, impersonate="chrome120", timeout=10)
    print(f"\n[{resp.status_code}] {resp.url}")
    if resp.status_code != 200:
        print(f"  Response: {resp.text[:300]}")
        return None
    data = resp.json()
    # Dump full structure for first call to understand format
    print(f"  Top-level keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
    return data


def extract_titles(data, label):
    """Extract and print titles from response."""
    if data is None:
        return []

    items = None
    if isinstance(data, dict):
        for k in ['data', 'result']:
            if k in data:
                sub = data[k]
                if isinstance(sub, list):
                    items = sub
                    break
                if isinstance(sub, dict):
                    for sk in ['list', 'posts', 'notices', 'announcements', 'items', 'contents']:
                        if sk in sub:
                            items = sub[sk]
                            break
                if items:
                    break
        if not items:
            for k in ['list', 'posts', 'notices', 'announcements', 'items']:
                if k in data and isinstance(data[k], list):
                    items = data[k]
                    break

    if not items:
        print(f"  Could not extract items. Raw: {json.dumps(data, ensure_ascii=False)[:500]}")
        return []

    print(f"  Found {len(items)} items. Keys per item: {list(items[0].keys()) if items else 'none'}")
    titles = []
    for item in items[:10]:
        title = item.get("title", item.get("text", item.get("name", "NO_TITLE")))
        item_id = item.get("id", item.get("noticeId", "?"))
        titles.append((item_id, title))
        paren = "← HAS ()" if title.rstrip().endswith(")") else "← CLEAN ★"
        print(f"    [{item_id}] {title}  {paren}")

    return titles


def main():
    print("=" * 100)
    print("ENDPOINT 1: /api/v1/notices")
    print("=" * 100)
    data1 = fetch(
        "https://api-manager.upbit.com/api/v1/notices",
        {"page": 1, "per_page": 20}
    )
    titles1 = extract_titles(data1, "notices")

    print("\n" + "=" * 100)
    print("ENDPOINT 2: /api/v1/announcements (os=web, category=all)")
    print("=" * 100)
    data2 = fetch(
        "https://api-manager.upbit.com/api/v1/announcements",
        {"os": "web", "page": 1, "per_page": 20, "category": "all"}
    )
    titles2 = extract_titles(data2, "announcements")

    print("\n" + "=" * 100)
    print("ENDPOINT 3: /api/v1/disclosure (project-team.upbit.com)")
    print("=" * 100)
    data3 = fetch(
        "https://project-team.upbit.com/api/v1/disclosure",
        {"region": "kr", "per_page": 20}
    )
    titles3 = extract_titles(data3, "disclosure")

    # Side by side comparison for matching IDs
    if titles1 and titles2:
        print("\n" + "=" * 100)
        print("SIDE-BY-SIDE COMPARISON (matching IDs)")
        print("=" * 100)
        dict1 = {str(t[0]): t[1] for t in titles1}
        dict2 = {str(t[0]): t[1] for t in titles2}
        common_ids = set(dict1.keys()) & set(dict2.keys())
        if common_ids:
            for cid in sorted(common_ids):
                t1 = dict1[cid]
                t2 = dict2[cid]
                diff = "SAME" if t1 == t2 else "DIFFERENT ★★★"
                print(f"\n  ID {cid}:")
                print(f"    notices:       {t1}")
                print(f"    announcements: {t2}")
                print(f"    → {diff}")
        else:
            print("  No matching IDs found between notices and announcements.")
            print(f"  Notices IDs: {list(dict1.keys())[:5]}")
            print(f"  Announcements IDs: {list(dict2.keys())[:5]}")

    # Dump full first item from each for complete field comparison
    print("\n" + "=" * 100)
    print("FULL FIRST ITEM DUMP")
    print("=" * 100)
    for label, data in [("notices", data1), ("announcements", data2), ("disclosure", data3)]:
        if data is None:
            continue
        items = None
        if isinstance(data, dict):
            for k in ['data', 'result']:
                if k in data:
                    sub = data[k]
                    if isinstance(sub, list):
                        items = sub
                        break
                    if isinstance(sub, dict):
                        for sk in ['list', 'posts', 'notices', 'announcements', 'items', 'contents']:
                            if sk in sub:
                                items = sub[sk]
                                break
                    if items:
                        break
            if not items:
                for k in ['list', 'posts', 'notices', 'announcements', 'items']:
                    if k in data and isinstance(data[k], list):
                        items = data[k]
                        break
        if items:
            print(f"\n  [{label}] First item:")
            print(f"  {json.dumps(items[0], ensure_ascii=False, indent=4)}")


if __name__ == "__main__":
    main()
