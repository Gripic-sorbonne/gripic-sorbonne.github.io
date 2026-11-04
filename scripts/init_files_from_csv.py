# import csv
# from pathlib import Path
# import os
# import re
# import shutil
# import uuid
# import unicodedata

# # Directorios principales
# DATA_DIR: Path = Path("../") / "data" 
# IMAGES_DIR: Path = Path("./inputs/images")

# IGNORE_EVENT_COLUMNS = ["Sequentiel",]
# SPLIT_PATTERN: str = r"\s|\'|\-|\_|«|»|,"


# def get_last_name(full_name: str) -> str:
#     parts = full_name.strip().split()
#     return parts[-1] if parts else full_name


# def clean_folder_name(name: str) -> str:
#     invalid_chars = r'<>:[]+"/\\|?«»*'
#     cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", " ", name)
#     cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
#     cleaned_name = re.sub(r"_+", "_", cleaned_name)
#     return cleaned_name.strip("_")[:90].lower()


# def normalize_title(title: str) -> str:
#     return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", title.lower())).strip()


# def get_field(row_dict: dict, *keys: str, default: str = "") -> str:
#     """Helper to retrieve a dict value checking multiple key variations (case-insensitive)."""
#     for k in keys:
#         if k in row_dict and row_dict[k]:
#             return row_dict[k].strip()
#         for dict_key in row_dict.keys():
#             if dict_key.lower() == k.lower() and row_dict[dict_key]:
#                 return row_dict[dict_key].strip()
#     return default


# def make_yaml_header_event(title: str, author: str, abstract: str, image_filename: str, event_date: str) -> str:
#     clean_title = title.replace('"', '\\"').replace('\n', ' ')
#     clean_author = author.replace('"', '\\"').replace('\n', ' ')
#     clean_abstract = abstract.replace('"', '\\"').replace('\n', ' ')
    
#     year = event_date.split("-")[0] if event_date else "Unknown"

#     header = (f"---\n" +
#               f"uuid: {uuid.uuid4()}\n" +
#               f"title: \"{clean_title}\"\n" +
#               f"author: \"{clean_author}\"\n" +
#               f"date: \"{event_date}\"\n" +
#               f"year: \"{year}\"\n" +
#               f"event: true\n")
#     if image_filename:
#         header += f"image: \"{image_filename}\"\n"
#     header += (f"abstract: \"{clean_abstract}\"\n" +
#                f"---\n\n")
#     return header


# def generate_markdown_page_event(event_dict: dict, main_header: str, author_header: str, abstract_header: str, image_filename: str, event_date: str):
#     title = get_field(event_dict, main_header)
#     author = get_field(event_dict, author_header)
#     abstract = get_field(event_dict, abstract_header)

#     md_page = make_yaml_header_event(
#         title=title, author=author, abstract=abstract, image_filename=image_filename, event_date=event_date
#     )

#     if image_filename:
#         md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

#     for key, val in event_dict.items():
#         if val != "" and key not in IGNORE_EVENT_COLUMNS and key not in [main_header, author_header, abstract_header]:
#             md_page += f"## {key}\n\n {val}\n\n"

#     return md_page


# def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
#     global EVENT_DIR
    
#     # Rutas centralizadas usando IMAGES_DIR
#     events_img_dir = IMAGES_DIR / "events"
    
#     with open(csv_file, mode="r", encoding="utf-8") as f:
#         reader = csv.DictReader(f, delimiter=";")
#         for row in reader:
#             d, m, y = row['Date'].split('/')
#             date_str = f'{y}-{m}-{d}'
#             title_raw = get_field(row, main_header)
#             if not title_raw:
#                 continue

#             title: str = clean_folder_name(title_raw)
#             folder_name = date_str + "_" + title
#             event_subdir: Path = EVENT_DIR / folder_name
#             event_subdir.mkdir(parents=True, exist_ok=True)

#             img_filename = get_field(row, photo_header, "image", "photo", default="")
#             target_image = "no_event.webp"

#             source_img_path = events_img_dir / img_filename
#             default_img_path = events_img_dir / "no_event.webp"

#             if img_filename and source_img_path.exists():
#                 shutil.copy(str(source_img_path), str(event_subdir / img_filename))
#                 target_image = img_filename
#             elif default_img_path.exists():
#                 shutil.copy(str(default_img_path), str(event_subdir / 'no_event.webp'))
#             elif os.path.exists('./no_event.webp'):
#                 shutil.copy('./no_event.webp', str(event_subdir / 'no_event.webp'))

#             with (event_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
#                 md_file.write(generate_markdown_page_event(
#                     event_dict=row, 
#                     main_header=main_header,
#                     author_header=author_header, 
#                     abstract_header=abstract_header, 
#                     image_filename=target_image,
#                     event_date=date_str
#                 ))


# def normalize_for_match(s: str) -> set:
#     s = unicodedata.normalize('NFD', s)
#     s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
#     return set(re.findall(r'[a-z0-9]+', s.lower()))

# def csv_to_markdown_categories(csv_file_categories):
#     global IMAGES_DIR
#     default_img_src = IMAGES_DIR / "events" / "no_event.webp"

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

#             # Copiar imagen por defecto a la categoría para que Gatsby la reconozca como File @fileByRelativePath
#             target_image = "no_event.webp"
#             if default_img_src.exists():
#                 shutil.copy(str(default_img_src), str(folder_path / target_image))

#             index_file_path = folder_path / 'index.md'
            
#             with index_file_path.open(mode='w', encoding='utf-8') as index_file:
#                 header = (f"---\n" +
#                           f"uuid: {uuid.uuid4()}\n" +
#                           f"title: \"{name.capitalize()}\"\n" +
#                           f"menuGroup: \"{group_raw}\"\n" +
#                           f"image: \"{target_image}\"\n" +
#                           f"---\n")
#                 content = header + description
#                 index_file.write(content)

            
# csv_file_event = "./inputs/calendar.csv"
# csv_file_categories = "./inputs/categories.csv"

# csv_to_markdown_categories(csv_file_categories)
# csv_to_markdown_events(csv_file_event)

# print("Folders and Markdown files created successfully using IMAGES_DIR.")

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


def clean_folder_name(name: str) -> str:
    invalid_chars = r'<>:[]+"/\\|?«»*'
    cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", " ", name)
    cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
    cleaned_name = re.sub(r"_+", "_", cleaned_name)
    return cleaned_name.strip("_")[:90].lower()


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s.lower())


def get_field(row_dict: dict, *keys: str, default: str = "") -> str:
    for k in keys:
        if k in row_dict and row_dict[k]:
            return row_dict[k].strip()
        for dict_key in row_dict.keys():
            if dict_key.lower() == k.lower() and row_dict[dict_key]:
                return row_dict[dict_key].strip()
    return default


def find_matching_csv(submenu_name: str, inputs_dir: Path) -> Path:
    target_norm = normalize_text(submenu_name)
    if not inputs_dir.exists():
        return None
        
    for file in inputs_dir.glob("*.csv"):
        if normalize_text(file.stem) == target_norm:
            return file
    return None


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
        if val != "" and not key.startswith('_') and key not in IGNORE_EVENT_COLUMNS and key not in [main_header, author_header, abstract_header]:
            md_page += f"## {key}\n\n {val}\n\n"

    return md_page


def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
    global EVENT_DIR
    if not os.path.exists(csv_file):
        return
    
    events_img_dir = IMAGES_DIR / "events"
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            date_raw = get_field(row, "Date")
            if not date_raw or '/' not in date_raw:
                continue
            d, m, y = date_raw.split('/')
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


def generate_markdown_page_card(row_dict: dict, image_filename: str, columns_to_show: list, metadata_fields: dict):
    header = f"---\nuuid: {uuid.uuid4()}\n"
    
    for meta_key, meta_val in metadata_fields.items():
        clean_meta_val = str(meta_val).replace('"', '\\"').replace('\n', ' ')
        header += f"{meta_key}: \"{clean_meta_val}\"\n"

    if image_filename:
        header += f'image: "{image_filename}"\n'
    
    header += f"---\n\n"
    md_page = header

    if image_filename and image_filename != "no_img_gripic.webp":
        md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

    for key in columns_to_show:
        val = row_dict.get(key, "")
        if val != "" and not key.startswith('_'):
            md_page += f"## {key}\n\n {val}\n\n"

    return md_page


# def csv_to_markdown_cards_or_longcards(csv_file: Path, target_dir: Path, card_type: str):
#     if not csv_file or not csv_file.exists():
#         return

#     prefix_name = "longcard" if "long" in card_type.lower() else "card"
#     default_card_img_path = IMAGES_DIR / "no_img_gripic.webp"

#     with open(csv_file, mode="r", encoding="utf-8") as f:
#         reader = list(csv.DictReader(f, delimiter=";"))
#         if not reader:
#             return

#         all_columns = list(reader[0].keys())

#         for idx, row in enumerate(reader, start=1):
#             metadata_fields = {}
#             columns_to_show = []
#             first_meta_val = ""
#             img_filename = ""

#             for col in all_columns:
#                 val = row.get(col, "").strip()
#                 if col.startswith('_'):
#                     clean_key = col.lstrip('_').lower()
#                     if clean_key in ['image', 'images', 'photo']:
#                         img_filename = val
#                     else:
#                         metadata_fields[clean_key] = val
#                         if not first_meta_val and val:
#                             first_meta_val = clean_folder_name(val)
#                 else:
#                     columns_to_show.append(col)

#             if first_meta_val:
#                 folder_title_part = f"{idx:02d}_{first_meta_val}"
#             else:
#                 folder_title_part = f"{idx:02d}"

#             sub_folder = target_dir / f"{prefix_name}_{folder_title_part}"
#             sub_folder.mkdir(parents=True, exist_ok=True)

#             target_image = "no_img_gripic.webp"
#             source_img_path = IMAGES_DIR / img_filename if img_filename else None

#             if img_filename and source_img_path and source_img_path.exists():
#                 shutil.copy(str(source_img_path), str(sub_folder / img_filename))
#                 target_image = img_filename
#             elif default_card_img_path.exists():
#                 shutil.copy(str(default_card_img_path), str(sub_folder / "no_img_gripic.webp"))
#                 target_image = "no_img_gripic.webp"

#             with (sub_folder / "index.md").open(mode="w", encoding="utf-8") as md_file:
#                 md_file.write(generate_markdown_page_card(
#                     row_dict=row,
#                     image_filename=target_image,
#                     columns_to_show=columns_to_show,
#                     metadata_fields=metadata_fields
#                 ))
def csv_to_markdown_cards_or_longcards(csv_file: Path, target_dir: Path, card_type: str):
    if not csv_file or not csv_file.exists():
        return

    prefix_name = "longcard" if "long" in card_type.lower() else "card"
    default_card_img_path = IMAGES_DIR / "no_img_GRIPIC.webp"

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f, delimiter=";"))
        if not reader:
            return

        all_columns = list(reader[0].keys())

        for idx, row in enumerate(reader, start=1):
            metadata_fields = {}
            columns_to_show = []
            first_meta_val = ""
            img_filename = ""

            for col in all_columns:
                val = row.get(col, "").strip()
                if col.startswith('_'):
                    clean_key = col.lstrip('_').lower()
                    if clean_key in ['image', 'images', 'photo']:
                        img_filename = val
                    else:
                        metadata_fields[clean_key] = val
                        if not first_meta_val and val:
                            first_meta_val = clean_folder_name(val)
                else:
                    columns_to_show.append(col)

            if first_meta_val:
                folder_title_part = f"{idx:02d}_{first_meta_val}"
            else:
                folder_title_part = f"{idx:02d}"

            sub_folder = target_dir / f"{prefix_name}_{folder_title_part}"
            sub_folder.mkdir(parents=True, exist_ok=True)

            target_image = "no_img_GRIPIC.webp"
            source_img_path = IMAGES_DIR / img_filename if img_filename else None

            if img_filename and source_img_path and source_img_path.exists():
                # Extraer solo el nombre del archivo (ej. no_publica.webp) ignorando las subcarpetas de origen
                pure_img_name = Path(img_filename).name
                destination_img_path = sub_folder / pure_img_name
                
                shutil.copy(str(source_img_path), str(destination_img_path))
                target_image = pure_img_name
            elif default_card_img_path.exists():
                shutil.copy(str(default_card_img_path), str(sub_folder / "no_img_GRIPIC.webp"))
                target_image = "no_img_GRIPIC.webp"

            with (sub_folder / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_card(
                    row_dict=row,
                    image_filename=target_image,
                    columns_to_show=columns_to_show,
                    metadata_fields=metadata_fields
                ))


def csv_to_markdown_categories(csv_file_categories):
    global EVENT_DIR
    # Respaldo general por defecto para categorías normales en la raíz de IMAGES_DIR
    default_general_img = IMAGES_DIR / "no_img_gripic.webp"
    default_event_img = IMAGES_DIR / "events" / "no_event.webp"
    inputs_dir = Path("./inputs")

    with open(csv_file_categories, newline='', encoding='utf-8') as file:
        reader = list(csv.DictReader(file, delimiter=';'))
        
        for idx, row in enumerate(reader, start=1):
            group_raw = row['groupe'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            type_ = row['type'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip().lower()
            name = row['nom'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            description = row['description']

            group_clean = clean_folder_name(group_raw)
            clean_name = clean_folder_name(name)
            
            prefix = f"{idx:02d}"
            folder_name = f"{prefix}_{group_clean}__{type_}__{clean_name}"
            folder_path = DATA_DIR / folder_name

            is_event_folder = "événements" in folder_name.lower()
            if is_event_folder:
                EVENT_DIR = folder_path

            folder_path.mkdir(exist_ok=True, parents=True)

            # Asignar imagen por defecto correcta según el tipo de carpeta
            target_image = "no_img_gripic.webp"
            if is_event_folder and default_event_img.exists():
                shutil.copy(str(default_event_img), str(folder_path / "no_event.webp"))
                target_image = "no_event.webp"
            elif default_general_img.exists():
                shutil.copy(str(default_general_img), str(folder_path / "no_img_gripic.webp"))
                target_image = "no_img_gripic.webp"

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

            sub_csv = find_matching_csv(name, inputs_dir)
            if sub_csv:
                csv_to_markdown_cards_or_longcards(sub_csv, folder_path, type_)


csv_file_event = "./inputs/calendar.csv"
csv_file_categories = "./inputs/categories.csv"

if os.path.exists(csv_file_categories):
    csv_to_markdown_categories(csv_file_categories)

if os.path.exists(csv_file_event):
    csv_to_markdown_events(csv_file_event)

print("Folders and Markdown files created successfully with correct default images mapping.")























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


def clean_folder_name(name: str) -> str:
    invalid_chars = r'<>:[]+"/\\|?«»*'
    cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", " ", name)
    cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
    cleaned_name = re.sub(r"_+", "_", cleaned_name)
    return cleaned_name.strip("_")[:90].lower()


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s.lower())


def get_field(row_dict: dict, *keys: str, default: str = "") -> str:
    for k in keys:
        if k in row_dict and row_dict[k]:
            return row_dict[k].strip()
        for dict_key in row_dict.keys():
            if dict_key.lower() == k.lower() and row_dict[dict_key]:
                return row_dict[dict_key].strip()
    return default


def find_matching_csv(submenu_name: str, inputs_dir: Path) -> Path:
    target_norm = normalize_text(submenu_name)
    if not inputs_dir.exists():
        return None
        
    for file in inputs_dir.glob("*.csv"):
        if normalize_text(file.stem) == target_norm:
            return file
    return None


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
        if val != "" and not key.startswith('_') and key not in IGNORE_EVENT_COLUMNS and key not in [main_header, author_header, abstract_header]:
            md_page += f"## {key}\n\n {val}\n\n"

    return md_page


def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
    global EVENT_DIR
    if not os.path.exists(csv_file):
        return
    
    events_img_dir = IMAGES_DIR / "events"
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            date_raw = get_field(row, "Date")
            if not date_raw or '/' not in date_raw:
                continue
            d, m, y = date_raw.split('/')
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


def generate_markdown_page_card(row_dict: dict, image_filename: str, columns_to_show: list, metadata_fields: dict):
    header = f"---\nuuid: {uuid.uuid4()}\n"
    
    for meta_key, meta_val in metadata_fields.items():
        clean_meta_val = str(meta_val).replace('"', '\\"').replace('\n', ' ')
        
        # Corrección clave: Si la clave es 'tags', transformamos el texto en un arreglo YAML [String]
        if meta_key == 'tags':
            tags_list = [t.strip() for t in str(meta_val).replace(',', ' ').split() if t.strip()]
            formatted_tags = "[" + ", ".join([f'"{t}"' for t in tags_list]) + "]"
            header += f"{meta_key}: {formatted_tags}\n"
        else:
            header += f"{meta_key}: \"{clean_meta_val}\"\n"

    if image_filename:
        header += f'image: "{image_filename}"\n'
    
    header += f"---\n\n"
    md_page = header

    if image_filename and image_filename != "no_img_gripic.webp":
        md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

    for key in columns_to_show:
        val = row_dict.get(key, "")
        if val != "" and not key.startswith('_'):
            md_page += f"## {key}\n\n {val}\n\n"

    return md_page


def csv_to_markdown_cards_or_longcards(csv_file: Path, target_dir: Path, card_type: str):
    if not csv_file or not csv_file.exists():
        return

    prefix_name = "longcard" if "long" in card_type.lower() else "card"
    default_card_img_path = IMAGES_DIR / "no_img_GRIPIC.webp"

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f, delimiter=";"))
        if not reader:
            return

        all_columns = list(reader[0].keys())

        for idx, row in enumerate(reader, start=1):
            metadata_fields = {}
            columns_to_show = []
            first_meta_val = ""
            img_filename = ""

            for col in all_columns:
                val = row.get(col, "").strip()
                if col.startswith('_'):
                    clean_key = col.lstrip('_').lower()
                    if clean_key in ['image', 'images', 'photo']:
                        img_filename = val
                    else:
                        metadata_fields[clean_key] = val
                        if not first_meta_val and val:
                            first_meta_val = clean_folder_name(val)
                else:
                    columns_to_show.append(col)

            if first_meta_val:
                folder_title_part = f"{idx:02d}_{first_meta_val}"
            else:
                folder_title_part = f"{idx:02d}"

            sub_folder = target_dir / f"{prefix_name}_{folder_title_part}"
            sub_folder.mkdir(parents=True, exist_ok=True)

            target_image = "no_img_GRIPIC.webp"
            source_img_path = IMAGES_DIR / img_filename if img_filename else None

            if img_filename and source_img_path and source_img_path.exists():
                pure_img_name = Path(img_filename).name
                destination_img_path = sub_folder / pure_img_name
                
                shutil.copy(str(source_img_path), str(destination_img_path))
                target_image = pure_img_name
            elif default_card_img_path.exists():
                shutil.copy(str(default_card_img_path), str(sub_folder / "no_img_GRIPIC.webp"))
                target_image = "no_img_GRIPIC.webp"

            with (sub_folder / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_card(
                    row_dict=row,
                    image_filename=target_image,
                    columns_to_show=columns_to_show,
                    metadata_fields=metadata_fields
                ))


def csv_to_markdown_categories(csv_file_categories):
    global EVENT_DIR
    default_general_img = IMAGES_DIR / "no_img_gripic.webp"
    default_event_img = IMAGES_DIR / "events" / "no_event.webp"
    inputs_dir = Path("./inputs")

    with open(csv_file_categories, newline='', encoding='utf-8') as file:
        reader = list(csv.DictReader(file, delimiter=';'))
        
        for idx, row in enumerate(reader, start=1):
            group_raw = row['groupe'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            type_ = row['type'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip().lower()
            name = row['nom'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
            description = row['description']

            group_clean = clean_folder_name(group_raw)
            clean_name = clean_folder_name(name)
            
            prefix = f"{idx:02d}"
            folder_name = f"{prefix}_{group_clean}__{type_}__{clean_name}"
            folder_path = DATA_DIR / folder_name

            is_event_folder = "événements" in folder_name.lower()
            if is_event_folder:
                EVENT_DIR = folder_path

            folder_path.mkdir(exist_ok=True, parents=True)

            target_image = "no_img_gripic.webp"
            if is_event_folder and default_event_img.exists():
                shutil.copy(str(default_event_img), str(folder_path / "no_event.webp"))
                target_image = "no_event.webp"
            elif default_general_img.exists():
                shutil.copy(str(default_general_img), str(folder_path / "no_img_gripic.webp"))
                target_image = "no_img_gripic.webp"

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

            sub_csv = find_matching_csv(name, inputs_dir)
            if sub_csv:
                csv_to_markdown_cards_or_longcards(sub_csv, folder_path, type_)


csv_file_event = "./inputs/calendar.csv"
csv_file_categories = "./inputs/categories.csv"

if os.path.exists(csv_file_categories):
    csv_to_markdown_categories(csv_file_categories)

if os.path.exists(csv_file_event):
    csv_to_markdown_events(csv_file_event)

print("Folders and Markdown files created successfully with correct default images mapping.")
