import csv
import json
from pathlib import Path


def get_webp_filename(photo_path):
    """Extracts the base filename of the photo and forces the .webp extension."""
    if not photo_path:
        return ""

    filename = Path(photo_path).stem  # Gets the name without extension or path
    return f"{filename}.webp"


def generate_username(full_name, index):
    """Generates a fallback username if none exists in the JSON data."""
    if not full_name:
        return f"user{index}"

    parts = full_name.lower().split()
    if len(parts) >= 2:
        username = parts[0][0] + parts[-1]
    else:
        username = parts[0]

    # Clean special characters from username
    cleaned_username = "".join(c for c in username if c.isalnum())
    return cleaned_username or f"user{index}"


def generate_info_contact_block(member):
    """Builds a Markdown block containing contact information and available links."""
    lines = []

    # Email
    email = member.get("email")
    if email:
        lines.append(f"* **Email:** [{email}](mailto:{email})")

    # Social Networks and Academic Profiles
    social_links = []
    links_map = {
        "linkedin": "LinkedIn",
        "hal": "HAL",
        "orcid": "ORCID",
        "twitter": "Twitter",
        "researchgate": "ResearchGate",
    }

    for key, label in links_map.items():
        url = member.get(key)
        if url:
            social_links.append(f"[{label}]({url})")

    if social_links:
        lines.append(f"* **Profils:** {' | '.join(social_links)}")

    # Documents (CV)
    cv_url = member.get("cv_url")
    if cv_url:
        lines.append(f"* **CV:** [Télécharger le CV]({cv_url})")

    return "\n".join(lines)


def convert_json_to_csv(json_file_path, output_csv_path):
    # 1. Load the JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        members = json.load(f)

    # 2. Preliminary exploration: Dynamically discover ALL unique sections in the dataset
    dynamic_sections = set()
    for member in members:
        sections = member.get("sections", {})
        if isinstance(sections, dict):
            for section_name in sections.keys():
                if section_name and section_name.strip():
                    dynamic_sections.add(section_name.strip())

    # Convert to a sorted list to maintain consistent column ordering
    sorted_sections = sorted(list(dynamic_sections))

    # 3. Define CSV headers matching old structure + semicolon delimiter expectation
    headers = [
        "Nom d'utilisateur",
        "Prénom et Nom",
        "Fonction",
        "Photo",
        "Informations et Contact",
    ] + sorted_sections

    # 4. Process and write rows
    rows = []
    for idx, member in enumerate(members, start=1):
        full_name = member.get("full_name", "").strip()
        username = member.get("username") or generate_username(full_name, idx)
        role = member.get("role", "").strip()
        photo = get_webp_filename(member.get("photo_path"))
        info_contact = generate_info_contact_block(member)

        row = {
            "Nom d'utilisateur": username,
            "Prénom et Nom": full_name,
            "Fonction": role,
            "Photo": photo,
            "Informations et Contact": info_contact,
        }

        # Map dynamic sections
        member_sections = member.get("sections", {})
        if isinstance(member_sections, dict):
            for section_name in sorted_sections:
                content = member_sections.get(section_name, "")
                if content and str(content).strip():
                    row[section_name] = str(content).strip()
                else:
                    row[section_name] = ""
        else:
            for section_name in sorted_sections:
                row[section_name] = ""

        rows.append(row)

    # 5. Save to CSV using semicolon delimiter ';'
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Success! Processed {len(members)} members.")
    print(f"Total detected columns: {len(headers)}")
    print(f"File generated at: {output_csv_path}")


if __name__ == "__main__":
    convert_json_to_csv("members_dataset.json", "members.csv")