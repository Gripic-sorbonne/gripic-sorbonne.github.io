"""
Fetches member photo URLs from kit-117.sorbonne-universite.fr
and adds them to members.csv in the Photo column.
"""

import csv
import re
import ssl
import urllib.request
import unicodedata


BASE_URL = "https://kit-117.sorbonne-universite.fr"
CSV_PATH = "/Users/jungmin/Desktop/gripic_sorbonne/gripic-sorbonne.github.io/scripts/inputs/members.csv"
OUTPUT_PATH = "scripts/inputs/members_with_photos.csv"


def normalize(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().strip()


def slug_to_name_parts(slug):
    return set(re.split(r"[\s\-']+", normalize(slug)))


def fetch_html(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; research-scraper/1.0)"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode("utf-8")


def extract_member_photos(html):
    pattern = r'class="profile__img img-cover"\s+href="/membres/([^"]+)">\s*<img[^>]+data-src="([^"]+)"'
    matches = re.findall(pattern, html)
    return [(slug, BASE_URL + url) for slug, url in matches]


def name_to_parts(name):
    n = normalize(name)
    parts = re.split(r"[\s\-']+", n)
    result = set(p for p in parts if p)
    for m in re.finditer(r"(\w+)'(\w+)", n):
        result.add(m.group(1) + m.group(2))
    return result


def match_csv_name(csv_name, slug_parts):
    csv_parts = name_to_parts(csv_name)
    overlap = csv_parts & slug_parts
    return len(overlap) >= 2


def main():
    all_members_photos = []
   
    url = f"https://kit-117.sorbonne-universite.fr/membres?field_tag=&field_person_type%5B0%5D=291&page=6"
    print(f"Fetching page: {url} ...")
    html = fetch_html(url)
    photos = extract_member_photos(html)
    print(f"  Found {len(photos)} photos on page.")
    all_members_photos.extend(photos)

    print(f"\nTotal photos collected: {len(all_members_photos)}")
    for slug, url in all_members_photos:
        print(f"  {slug} => {url}")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames
        rows = list(reader)

    matched = 0
    for row in rows:
        csv_name = row.get("Prénom et Nom", "")
        for slug, url in all_members_photos:
            slug_parts = slug_to_name_parts(slug)
            if match_csv_name(csv_name, slug_parts):
                row["Photo"] = url
                matched += 1
                print(f"  Matched: '{csv_name}' => {url}")
                break

    print(f"\nMatched {matched}/{len(rows)} members.")

    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
