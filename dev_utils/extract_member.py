import json
import os
import re
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Global paths
CACHE_DIR = "cache_html"
JSON_PATH = "members_dataset.json"
BASE_URL = "https://kit-117.sorbonne-universite.fr"


def extract_profile_data(html_content, base_info=None):
    """Extract structured information from HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    profile_data = base_info.copy() if base_info else {}

    # Target specific profile info container to avoid header/footer elements
    info_container = soup.select_one("div.field-info")

    # 1. Email extraction
    email = None
    if info_container:
        mailto_link = info_container.find(
            "a", href=re.compile(r"^mailto:", re.IGNORECASE)
        )
        if mailto_link and mailto_link.get("href"):
            clean_href = mailto_link["href"].replace("mailto:", "").strip()
            email_match = re.search(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", clean_href
            )
            if email_match:
                email = email_match.group(0)

    # Fallback search across raw text if container fails
    if not email:
        raw_text = soup.get_text()
        email_match = re.search(
            r"[a-zA-Z0-9._%+-]+@(sorbonne-universite|celsa)\.[a-zA-Z]{2,}",
            raw_text,
            re.IGNORECASE,
        )
        if email_match:
            email = email_match.group(0)

    profile_data["email"] = email

    # 2. Social Media Links extraction
    social_platforms = {
        "linkedin": r"linkedin\.com/(in|pub|profile)",
        "twitter": r"(twitter\.com|x\.com)",
        "facebook": r"facebook\.com",
        "instagram": r"instagram\.com",
        "youtube": r"youtube\.com",
        "researchgate": r"researchgate\.net",
        "academia": r"academia\.edu",
        "hal": r"hal\.science|hal\.archives-ouvertes\.fr",
        "github": r"github\.com",
        "orcid": r"orcid\.org",
    }

    social_data = {platform: None for platform in social_platforms}

    if info_container:
        links = info_container.find_all("a", href=True)
        for link in links:
            href = link["href"].strip()
            for platform, pattern in social_platforms.items():
                if re.search(pattern, href, re.IGNORECASE):
                    if not social_data[platform]:
                        social_data[platform] = href

    # Populate top-level dictionary keys for each social network
    for platform, url in social_data.items():
        profile_data[platform] = url

    # 3. CV Download Link extraction
    cv_url = None
    # Buscar etiqueta 'a' que tenga el atributo 'download' o cuyo 'href' contenga 'CV'
    cv_link = soup.find("a", download=True) or soup.find(
        "a", href=re.compile(r"/CV%20|/CV_", re.IGNORECASE)
    )

    if cv_link and cv_link.get("href"):
        raw_cv_href = cv_link["href"].strip()
        cv_url = urljoin(BASE_URL, raw_cv_href)

    profile_data["cv_url"] = cv_url

    # 4. Research topics extraction
    research_topics = []
    research_header = soup.find(
        lambda tag: tag.name in ["h2", "h3", "h4"]
        and "Thématiques de recherche" in tag.text
    )

    if research_header:
        parent_container = research_header.find_parent(
            ["div", "section", "article"]
        )
        if parent_container:
            list_items = parent_container.select("ul li, ol li, .field__item")
            for item in list_items:
                clean_text = item.get_text(strip=True)
                if clean_text and clean_text not in research_topics:
                    research_topics.append(clean_text)

    profile_data["research_topics"] = research_topics

    # 5. Dynamic section extraction
    sections_data = {}
    headers = soup.find_all(["h2", "h3", "h4"])

    for header in headers:
        header_title = header.get_text(strip=True)
        if not header_title or header_title in [
            "Retrouvez-nous !",
            "Navigation principal",
            "Pied de page",
        ]:
            continue

        content_block = []
        sibling = header.find_next_sibling()

        while sibling and sibling.name not in ["h2", "h3", "h4"]:
            text = sibling.get_text(separator="\n", strip=True)
            if text:
                content_block.append(text)
            sibling = sibling.find_next_sibling()

        if content_block:
            sections_data[header_title] = "\n".join(content_block)

    profile_data["sections"] = sections_data

    return profile_data


def process_files(target_index=None):
    if not os.path.exists(CACHE_DIR):
        print(f"[ERROR] Directory {CACHE_DIR} was not found.")
        return

    html_files = sorted(
        [f for f in os.listdir(CACHE_DIR) if f.endswith(".html")]
    )

    if not html_files:
        print("[ERROR] No HTML files were found in the folder.")
        return

    if target_index is not None:
        if 0 <= target_index < len(html_files):
            files_to_process = [html_files[target_index]]
            print(
                f"Processing index [{target_index}]: "
                f"{files_to_process[0]}"
            )
        else:
            print(
                f"[ERROR] Index out of range. Valid range: "
                f"0 to {len(html_files) - 1}"
            )
            return
    else:
        files_to_process = html_files
        print(f"Processing all files ({len(files_to_process)})...")

    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            dataset = json.load(f)
    else:
        dataset = []

    dataset_map = {item.get("slug"): item for item in dataset}

    for file_name in files_to_process:
        slug = file_name.replace(".html", "")
        file_path = os.path.join(CACHE_DIR, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        base_info = dataset_map.get(slug, {"slug": slug})

        updated_info = extract_profile_data(html_content, base_info)

        dataset_map[slug] = updated_info

    updated_dataset = list(dataset_map.values())

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_dataset, f, indent=2, ensure_ascii=False)

    print(f"[OK] {JSON_PATH} successfully updated.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
            process_files(n)
        except ValueError:
            print("[ERROR] The argument must be an integer.")
    else:
        process_files()