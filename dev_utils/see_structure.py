import os
import re
from collections import Counter
from bs4 import BeautifulSoup

CACHE_DIR = "cache_html"


def audit_html_files():
    if not os.path.exists(CACHE_DIR):
        print(f"The folder '{CACHE_DIR}' does not exist.")
        return

    html_files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".html")]
    total_files = len(html_files)
    print(f"--- Analyzing {total_files} cached HTML files ---\n")

    emails_found = 0
    class_counter = Counter()
    section_headers = Counter()
    email_sources = Counter()

    # Strict regex for detecting emails
    email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    for file_name in html_files:
        filepath = os.path.join(CACHE_DIR, file_name)
        with open(filepath, "rb") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # 1. Register Drupal/HTML classes in the main container
        main_content = soup.select_one("main, #main-content, article, .layout-content")
        if main_content:
            for tag in main_content.find_all(True):
                classes = tag.get("class", [])
                for cls in classes:
                    if cls.startswith("field") or "content" in cls or "profile" in cls or "detail" in cls:
                        class_counter[cls] += 1

        # 2. Internal section headers/titles (h2, h3, h4)
        for header in soup.find_all(["h2", "h3", "h4"]):
            text = header.get_text(strip=True)
            if text and len(text) < 50:
                section_headers[text] += 1

        # 3. Diagnose where the email is located (if it exists)
        raw_text = soup.get_text()
        found_in_file = False

        # A. mailto links
        mailto_tags = soup.select('a[href*="mailto:"]')
        for a in mailto_tags:
            match = email_regex.search(a["href"])
            if match:
                email_sources["href mailto"] += 1
                found_in_file = True

        # B. In plain text (excluding sharebar if we discard it)
        if not found_in_file:
            matches = email_regex.findall(raw_text)
            # Filter out generic template emails if any
            valid_matches = [m for m in matches if "sorbonne" in m or "celsa" in m]
            if valid_matches:
                email_sources["plain HTML text"] += 1
                found_in_file = True

        if found_in_file:
            emails_found += 1

    print(f"AUDIT RESULTS:")
    print(f"- Total profiles analyzed: {total_files}")
    print(f"- Profiles where email WAS FOUND: {emails_found} / {total_files}")
    print(f"- Profiles without a public email in the HTML: {total_files - emails_found}\n")

    print("DETECTED EMAIL SOURCES:")
    for source, count in email_sources.items():
        print(f"  • {source}: {count} pages")

    print("\nMOST COMMON CONTENT SECTIONS (H2/H3/H4 HEADERS):")
    for header, count in section_headers.most_common(15):
        print(f"  • '{header}': in {count} profiles")

    print("\nMOST REPEATED STRUCTURAL CLASSES:")
    for cls, count in class_counter.most_common(15):
        print(f"  • .{cls}: in {count} elements")


if __name__ == "__main__":
    audit_html_files()