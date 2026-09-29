import json
import csv
import re
from pathlib import Path

# Input JSON file paths
JSON_FILE_1 = "GRIPIC_last_publis.json"
JSON_FILE_2 = "20260609.bib.json"
OUTPUT_CSV = "./inputs/publications.csv"

# Publication type priority ranking for deduplication
TYPE_PRIORITY = {
    "article-journal": 1,
    "book": 2,
    "chapter": 3,
    "paper-conference": 4,
    "thesis": 5,
    "manuscript": 6
}


def normalize_title(title: str) -> str:
    """Normalizes publication title for strict deduplication matching."""
    if not title:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", title.lower())).strip()


def extract_date(issued_data: dict) -> str:
    """Extracts date-parts from JSON and converts into YYYY-MM-DD format."""
    if not issued_data or not isinstance(issued_data, dict):
        return "0000-01-01"
    
    date_parts = issued_data.get("date-parts", [])
    if not date_parts or not isinstance(date_parts, list) or not date_parts[0]:
        return "0000-01-01"
    
    parts = date_parts[0]
    year = str(parts[0]) if len(parts) > 0 and parts[0] else "0000"
    month = f"{parts[1]:02d}" if len(parts) > 1 and parts[1] else "01"
    day = f"{parts[2]:02d}" if len(parts) > 2 and parts[2] else "01"
    
    return f"{year}-{month}-{day}"


def extract_authors(author_list: list) -> str:
    """Formats list of author objects into a clean comma-separated string."""
    if not author_list or not isinstance(author_list, list):
        return ""
    
    authors = []
    for author in author_list:
        if isinstance(author, dict):
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            full_name = f"{given} {family}".strip()
            if full_name:
                authors.append(full_name)
    
    return ", ".join(authors)


def merge_and_deduplicate(data_sources: list) -> list:
    """Merges publication lists and removes duplicate items based on title and type."""
    grouped_pubs = {}

    for source in data_sources:
        for item in source:
            title = item.get("title", "").strip()
            if not title:
                continue

            norm_title = normalize_title(title)

            if norm_title not in grouped_pubs:
                grouped_pubs[norm_title] = item
            else:
                existing_item = grouped_pubs[norm_title]
                existing_priority = TYPE_PRIORITY.get(existing_item.get("type", ""), 99)
                current_priority = TYPE_PRIORITY.get(item.get("type", ""), 99)

                # Prioritize higher publication rank or richer record content
                if current_priority < existing_priority:
                    grouped_pubs[norm_title] = item
                elif current_priority == existing_priority:
                    if len(str(item)) > len(str(existing_item)):
                        grouped_pubs[norm_title] = item

    return list(grouped_pubs.values())


def convert_json_to_publications_csv():
    """Loads JSON datasets, deduplicates items, and writes outputs to publications.csv."""
    combined_raw_data = []

    # Load JSON source files
    for file_path in [JSON_FILE_1, JSON_FILE_2]:
        path = Path(file_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                combined_raw_data.append(json.load(f))
        else:
            print(f"Warning: File {file_path} not found.")

    # Deduplicate publications
    unique_publications = merge_and_deduplicate(combined_raw_data)

    # Ensure output directory exists
    output_path = Path(OUTPUT_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # CSV Header specification
    fieldnames = ["title", "authors", "date", "type", "url", "publisher", "container_title", "abstract"]

    # Write CSV file
    with open(output_path, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for pub in unique_publications:
            row = {
                "title": pub.get("title", "").strip(),
                "authors": extract_authors(pub.get("author", [])),
                "date": extract_date(pub.get("issued", {})),
                "type": pub.get("type", "").strip(),
                "url": pub.get("URL", "").strip(),
                "publisher": pub.get("publisher", "").strip(),
                "container_title": pub.get("container-title", "").strip(),
                "abstract": pub.get("abstract", "").strip()
            }
            writer.writerow(row)

    print(f"Successfully generated '{OUTPUT_CSV}' with {len(unique_publications)} unique records.")


if __name__ == "__main__":
    convert_json_to_publications_csv()