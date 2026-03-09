"""
Kaggle Discussion一覧スクレイピング (Playwright版)
コンペのディスカッションページからトピック一覧を取得する
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


COMP_URL = "https://www.kaggle.com/competitions/march-machine-learning-mania-2026/discussion"
OUTPUT_FILE = "snapshot_{}.json".format(datetime.now().strftime("%Y%m%d"))


def scrape_discussions():
    discussions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        print(f"Navigating to {COMP_URL}")
        page.goto(COMP_URL, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # Scroll to load more discussions
        for i in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Extract discussion topics
        # Kaggle discussion list items
        items = page.query_selector_all('li[class*="MuiListItem"]')
        if not items:
            # Fallback: try other selectors
            items = page.query_selector_all('[data-testid*="discussion"], [class*="discussion-list"] a, a[href*="/discussion/"]')

        print(f"Found {len(items)} potential discussion elements")

        # Extract links to discussion pages
        links = page.query_selector_all('a[href*="/discussion/"]')
        seen_urls = set()

        for link in links:
            href = link.get_attribute("href")
            if not href or "/discussion/" not in href:
                continue
            # Filter to only competition discussion links
            if "march-machine-learning-mania-2026" not in href:
                continue
            # Skip non-topic links (like "discussion" nav link itself)
            parts = href.rstrip("/").split("/")
            if parts[-1] == "discussion":
                continue

            full_url = f"https://www.kaggle.com{href}" if href.startswith("/") else href
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            # Get text content
            title = link.inner_text().strip()
            if not title or len(title) < 3:
                continue

            discussions.append({
                "title": title,
                "url": full_url,
                "scraped_at": datetime.now().isoformat(),
            })

        # Try to get additional metadata from the page
        print(f"Extracted {len(discussions)} discussion topics")

        # Save page HTML for debugging if needed
        # with open("debug_page.html", "w") as f:
        #     f.write(page.content())

        browser.close()

    # Save snapshot
    snapshot = {
        "competition": "march-machine-learning-mania-2026",
        "scraped_at": datetime.now().isoformat(),
        "total_topics": len(discussions),
        "discussions": discussions,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(discussions)} discussions to {OUTPUT_FILE}")
    return snapshot


if __name__ == "__main__":
    scrape_discussions()
