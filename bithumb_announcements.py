#!/usr/bin/env python3
"""
Bithumb Announcement Checker
Fetches the latest announcements from Bithumb (feed.bithumb.com/notice)
and displays the 10 most recent ones with their IDs.
"""

import json
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_announcements(count=10):
    """Fetch latest Bithumb announcements via feed.bithumb.com."""
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    url = "https://feed.bithumb.com/notice"
    resp = scraper.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    next_data = soup.find("script", id="__NEXT_DATA__")
    if not next_data:
        raise RuntimeError("Could not find __NEXT_DATA__ on the page")

    data = json.loads(next_data.string)
    notice_list = data["props"]["pageProps"]["noticeList"]

    # Sort by publication date (newest first) and skip pinned old ones
    notices = sorted(
        notice_list,
        key=lambda x: x["publicationDateTime"],
        reverse=True,
    )

    # Return the top `count` announcements
    return notices[:count]


def main():
    print("=" * 70)
    print("  BITHUMB - 10 Latest Announcements")
    print("=" * 70)

    announcements = fetch_announcements(10)

    for i, ann in enumerate(announcements, 1):
        ann_id = ann["id"]
        title = ann["title"]
        category = ann.get("categoryName1", "N/A")
        date = ann["publicationDateTime"]
        pinned = " [PINNED]" if ann.get("topFixYn") == "Y" else ""
        url = f"https://feed.bithumb.com/notice/{ann_id}"

        print(f"\n{i:2}. ID: {ann_id}{pinned}")
        print(f"    Category: {category}")
        print(f"    Title:    {title}")
        print(f"    Date:     {date}")
        print(f"    URL:      {url}")

    print("\n" + "=" * 70)
    print(f"  Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
