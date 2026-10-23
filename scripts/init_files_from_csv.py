import csv
from pathlib import Path
import os
import re
import shutil
import uuid
import unicodedata

# Directorios principales
DATA_DIR: Path = Path("../") / "data" 
IMAGES_DIR: Path = Path("./inputs/images")

IGNORE_EVENT_COLUMNS = ["Sequentiel",]
SPLIT_PATTERN: str = r"\s|\'|\-|\_|«|»|,"


def get_last_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[-1] if parts else full_name


def clean_folder_name(name: str) -> str:
    invalid_chars = r'<>:[]+"/\\|?«»*'
    cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", " ", name)
    cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
    cleaned_name = re.sub(r"_+", "_", cleaned_name)
    return cleaned_name.strip("_")[:90].lower()


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", title.lower())).strip()


def get_field(row_dict: dict, *keys: str, default: str = "") -> str:
    """Helper to retrieve a dict value checking multiple key variations (case-insensitive)."""
    for k in keys:
        if k in row_dict and row_dict[k]:
            return row_dict[k].strip()
        for dict_key in row_dict.keys():
            if dict_key.lower() == k.lower() and row_dict[dict_key]:
                return row_dict[dict_key].strip()
    return default


def make_yaml_header_event(title: str, author: str, abstract: str, image_filename: str, event_date: str) -> str:
    clean_title = title.replace('"', '\\"').replace('\n', ' ')
    clean_author = author.replace('"', '\\"').replace('\n', ' ')
    clean_abstract = abstract.replace('"', '\\"').replace('\n', ' ')
    
    year = event_date.split("-")[0] if event_date else "Unknown"

    header = (f"---\n" +
              f"uuid: {uuid.uuid4()}\n" +
              f"title: \"{clean_title}\"\n" +
              f"author: \"{clean_author}\"\n" +
              f"date: \"{event_date}\"\n" +
              f"year: \"{year}\"\n" +
              f"event: true\n")
    if image_filename:
        header += f"image: \"{image_filename}\"\n"
    header += (f"abstract: \"{clean_abstract}\"\n" +
               f"---\n\n")
    return header


def generate_markdown_page_event(event_dict: dict, main_header: str, author_header: str, abstract_header: str, image_filename: str, event_date: str):
    title = get_field(event_dict, main_header)
    author = get_field(event_dict, author_header)
    abstract = get_field(event_dict, abstract_header)

    md_page = make_yaml_header_event(
        title=title, author=author, abstract=abstract, image_filename=image_filename, event_date=event_date
    )

    if image_filename:
        md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

    for key, val in event_dict.items():
        if val != "" and key not in IGNORE_EVENT_COLUMNS and key not in [main_header, author_header, abstract_header]:
            md_page += f"## {key}\n\n {val}\n\n"

    return md_page


def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
    global EVENT_DIR
    
    # Rutas centralizadas usando IMAGES_DIR
    events_img_dir = IMAGES_DIR / "events"
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            d, m, y = row['Date'].split('/')
            date_str = f'{y}-{m}-{d}'
            title_raw = get_field(row, main_header)
            if not title_raw:
                continue

            title: str = clean_folder_name(title_raw)
            folder_name = date_str + "_" + title
            event_subdir: Path = EVENT_DIR / folder_name
            event_subdir.mkdir(parents=True, exist_ok=True)

            img_filename = get_field(row, photo_header, "image", "photo", default="")
            target_image = "no_event.webp"

            source_img_path = events_img_dir / img_filename
            default_img_path = events_img_dir / "no_event.webp"

            if img_filename and source_img_path.exists():
                shutil.copy(str(source_img_path), str(event_subdir / img_filename))
                target_image = img_filename
            elif default_img_path.exists():
                shutil.copy(str(default_img_path), str(event_subdir / 'no_event.webp'))
            elif os.path.exists('./no_event.webp'):
                shutil.copy('./no_event.webp', str(event_subdir / 'no_event.webp'))

            with (event_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_event(
                    event_dict=row, 
                    main_header=main_header,
                    author_header=author_header, 
                    abstract_header=abstract_header, 
                    image_filename=target_image,
                    event_date=date_str
                ))


def normalize_for_match(s: str) -> set:
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return set(re.findall(r'[a-z0-9]+', s.lower()))


# def csv_to_markdown_categories(csv_file_categories):
#     with open(csv_file_categories, newline='', encoding='utf-8') as file:
#         reader = list(csv.DictReader(file, delimiter=';'))
        
#         for idx, row in enumerate(reader, start=1):
#             group_raw = row['groupe'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
#             type_ = row['type'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
#             name = row['nom'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
#             description = row['description']
            
#             group_clean = clean_folder_name(group_raw)
#             clean_name = clean_folder_name(name)
            
#             prefix = f"{idx:02d}"
#             folder_name = f"{prefix}_{group_clean}__{type_}__{clean_name}"
#             folder_path = DATA_DIR / folder_name

#             if "événements" in folder_name:
#                 global EVENT_DIR
#                 EVENT_DIR = folder_path

#             folder_path.mkdir(exist_ok=True, parents=True)
#             index_file_path = folder_path / 'index.md'
            
#             with index_file_path.open(mode='w', encoding='utf-8') as index_file:
#                 header = (f"---\n" +
#                           f"uuid: {uuid.uuid4()}\n" +
#                           f"title: \"{name.capitalize()}\"\n" +
#                           f"menuGroup: \"{group_raw}\"\n" +
#                           f"---\n")
#                 content = header + description
#                 index_file.write(content)

def csv_to_markdown_categories(csv_file_categories):
    global IMAGES_DIR
    default_img_src = IMAGES_DIR / "events" / "no_event.webp"

    with open(csv_file_categories, newline='', encoding='utf-8') as file:
        reader = list(csv.DictReader(file, delimiter=';'))
        
        for idx, row in enumerate(reader, start=1):
            group_raw = row['groupe'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            type_ = row['type'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            name = row['nom'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            description = row['description']
            
            group_clean = clean_folder_name(group_raw)
            clean_name = clean_folder_name(name)
            
            prefix = f"{idx:02d}"
            folder_name = f"{prefix}_{group_clean}__{type_}__{clean_name}"
            folder_path = DATA_DIR / folder_name

            if "événements" in folder_name:
                global EVENT_DIR
                EVENT_DIR = folder_path

            folder_path.mkdir(exist_ok=True, parents=True)

            # Copiar imagen por defecto a la categoría para que Gatsby la reconozca como File @fileByRelativePath
            target_image = "no_event.webp"
            if default_img_src.exists():
                shutil.copy(str(default_img_src), str(folder_path / target_image))

            index_file_path = folder_path / 'index.md'
            
            with index_file_path.open(mode='w', encoding='utf-8') as index_file:
                header = (f"---\n" +
                          f"uuid: {uuid.uuid4()}\n" +
                          f"title: \"{name.capitalize()}\"\n" +
                          f"menuGroup: \"{group_raw}\"\n" +
                          f"image: \"{target_image}\"\n" +
                          f"---\n")
                content = header + description
                index_file.write(content)

            
csv_file_event = "./inputs/calendar.csv"
csv_file_categories = "./inputs/categories.csv"

csv_to_markdown_categories(csv_file_categories)
csv_to_markdown_events(csv_file_event)

print("Folders and Markdown files created successfully using IMAGES_DIR.")