"""
Kaggle Notebook一覧スクレイピング (Playwright版)
コンペのCodeページからノートブック一覧を取得する（Most Votesソート）
"""

import json
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

COMP_SLUG = "march-machine-learning-mania-2026"
CODE_URL = f"https://www.kaggle.com/competitions/{COMP_SLUG}/code?sortBy=voteCount"
OUTPUT_FILE = "snapshot_{}.json".format(datetime.now().strftime("%Y%m%d"))


def scrape_notebooks():
    notebooks = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        print(f"Navigating to {CODE_URL}")
        page.goto(CODE_URL, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # Scroll to load more notebooks
        for i in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            print(f"  Scroll {i+1}/10")

        # Extract notebook links
        links = page.query_selector_all('a[href*="/code/"]')
        seen_urls = set()

        for link in links:
            href = link.get_attribute("href")
            if not href or "/code/" not in href:
                continue
            # Filter: notebook links typically match /username/notebook-slug pattern
            # Skip nav links, competition code page itself, etc.
            if href.endswith("/code") or href.endswith("/code/"):
                continue
            # Skip fragment links
            if "#" in href:
                continue
            # Must have at least 2 path segments after /code/
            parts = href.strip("/").split("/")
            if len(parts) < 2:
                continue
            # Skip if it's the competition code page
            if COMP_SLUG in href and href.rstrip("/").endswith("/code"):
                continue

            full_url = f"https://www.kaggle.com{href}" if href.startswith("/") else href
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            title = link.inner_text().strip()
            if not title or len(title) < 3:
                continue
            # Skip navigation-like text
            if title.lower() in ("code", "new notebook", "filters"):
                continue

            notebooks.append({
                "title": title,
                "url": full_url,
            })

        print(f"Found {len(notebooks)} raw notebook links")

        # Now try to get structured data from list items
        # Look for notebook cards/items with metadata
        structured = []
        items = page.query_selector_all('li[class*="MuiListItem"], div[class*="kernel-list-item"], [data-testid*="kernel"]')
        print(f"Found {len(items)} structured list items")

        # Alternative: parse the entire page text for vote counts near notebook titles
        # Get all text content and try to associate votes with notebooks
        all_text = page.inner_text("body")

        # Try to extract vote info from the page using a more targeted approach
        # Look for upvote elements near each notebook link
        for nb in notebooks:
            # Try to find the parent container and extract metadata
            try:
                link_el = page.query_selector(f'a[href="{nb["url"].replace("https://www.kaggle.com", "")}"]')
                if link_el:
                    # Walk up to find the container
                    parent = link_el.evaluate_handle("el => el.closest('li') || el.closest('div[class*=\"list\"]') || el.parentElement.parentElement.parentElement")
                    if parent:
                        parent_text = parent.inner_text()
                        # Extract vote count (number near arrow_drop_up)
                        vote_match = re.search(r'arrow_drop_up\s*(\d+)', parent_text)
                        if vote_match:
                            nb["votes"] = int(vote_match.group(1))
                        else:
                            # Try just a standalone number at start
                            num_match = re.search(r'(\d+)\s*$', parent_text.split('\n')[0].strip())
                            if num_match:
                                nb["votes"] = int(num_match.group(1))

                        # Extract comment count
                        comment_match = re.search(r'comment\s*(\d+)', parent_text)
                        if comment_match:
                            nb["comments"] = int(comment_match.group(1))
            except Exception:
                pass

        # Sort by votes (descending), notebooks without votes at the end
        notebooks.sort(key=lambda x: x.get("votes", -1), reverse=True)

        browser.close()

    # Save snapshot
    snapshot = {
        "competition": COMP_SLUG,
        "scraped_at": datetime.now().isoformat(),
        "sort": "voteCount",
        "total_notebooks": len(notebooks),
        "notebooks": notebooks,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(notebooks)} notebooks to {OUTPUT_FILE}")

    # Print top 10
    print("\n=== Top Notebooks ===")
    for i, nb in enumerate(notebooks[:10]):
        votes = nb.get("votes", "?")
        print(f"  {i+1}. [{votes} votes] {nb['title'][:80]}")

    return snapshot


if __name__ == "__main__":
    scrape_notebooks()
