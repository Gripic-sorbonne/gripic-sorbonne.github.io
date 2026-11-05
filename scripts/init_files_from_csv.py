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

# # Incluimos variantes con y sin tilde para evitar que columnas técnicas aparezcan en el contenido
# IGNORE_EVENT_COLUMNS = ["Sequentiel", "Séquentiel", "Contact"]

# # Variable global protegida para los eventos
# EVENT_DIR = None


# def clean_folder_name(name: str) -> str:
#     invalid_chars = r'<>:[]+"/\\|?«»*'
#     cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", " ", name)
#     cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
#     cleaned_name = re.sub(r"_+", "_", cleaned_name)
#     return cleaned_name.strip("_")[:90].lower()


# def normalize_text(s: str) -> str:
#     if not s:
#         return ""
#     s = unicodedata.normalize('NFD', s)
#     s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
#     return re.sub(r'[^a-z0-9]', '', s.lower())


# def get_field(row_dict: dict, *keys: str, default: str = "") -> str:
#     for k in keys:
#         if k in row_dict and row_dict[k]:
#             return row_dict[k].strip()
#         for dict_key in row_dict.keys():
#             if dict_key.lower() == k.lower() and row_dict[dict_key]:
#                 return row_dict[dict_key].strip()
#     return default


# def find_matching_csv(submenu_name: str, inputs_dir: Path) -> Path:
#     target_norm = normalize_text(submenu_name)
#     if not inputs_dir.exists():
#         return None
        
#     for file in inputs_dir.glob("*.csv"):
#         if normalize_text(file.stem) == target_norm:
#             return file
#     return None


# def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
#     global EVENT_DIR
#     if not os.path.exists(csv_file):
#         return
    
#     # SALVAVIDAS: Si EVENT_DIR no fue asignado por categories.csv, lo creamos por defecto
#     if EVENT_DIR is None or not isinstance(EVENT_DIR, Path):
#         EVENT_DIR = DATA_DIR / "04_activite_scientifique__cards__evenements"
#         EVENT_DIR.mkdir(parents=True, exist_ok=True)
    
#     events_img_dir = IMAGES_DIR / "events"
#     default_event_img = events_img_dir / "no_event.webp"
    
#     with open(csv_file, mode="r", encoding="utf-8") as f:
#         reader = csv.DictReader(f, delimiter=";")
#         for row in reader:
#             date_raw = get_field(row, "Date", "_date")
#             if not date_raw:
#                 continue
            
#             # Normalizar fecha DD/MM/YYYY a YYYY-MM-DD
#             date_str = date_raw
#             if '/' in date_raw:
#                 parts = date_raw.split('/')
#                 if len(parts) == 3:
#                     d, m, y = parts
#                     date_str = f'{y}-{m}-{d}'

#             year = date_str.split("-")[0] if "-" in date_str else "Unknown"
            
#             title_raw = get_field(row, main_header, "Titre", "_titre", "Title", "_title")
#             if not title_raw:
#                 continue

#             title: str = clean_folder_name(title_raw)
#             folder_name = f"{date_str}_{title}"
#             event_subdir: Path = EVENT_DIR / folder_name
#             event_subdir.mkdir(parents=True, exist_ok=True)

#             img_filename = get_field(row, photo_header, "image", "photo", default="")
#             target_image = "no_event.webp"

#             source_img_path = events_img_dir / img_filename
#             default_path = events_img_dir / "no_event.webp"

#             if img_filename and source_img_path.exists():
#                 pure_img_name = Path(img_filename).name
#                 shutil.copy(str(source_img_path), str(event_subdir / pure_img_name))
#                 target_image = pure_img_name
#             elif default_path.exists():
#                 shutil.copy(str(default_path), str(event_subdir / 'no_event.webp'))
#                 target_image = "no_event.webp"

#             # Extraer campos principales con flexibilidad
#             author = get_field(row, author_header, "Organisateur(s)", "_author")
#             abstract = get_field(row, abstract_header, "Descriptif", "_abstract")
            
#             clean_title = title_raw.replace('"', '\\"').replace('\n', ' ')
#             clean_author = author.replace('"', '\\"').replace('\n', ' ')
#             clean_abstract = abstract.replace('"', '\\"').replace('\n', ' ')

#             # Construir Frontmatter YAML asegurando event: true
#             header = (f"---\n" +
#                       f"uuid: {uuid.uuid4()}\n" +
#                       f"title: \"{clean_title}\"\n" +
#                       f"author: \"{clean_author}\"\n" +
#                       f"date: \"{date_str}\"\n" +
#                       f"year: \"{year}\"\n" +
#                       f"event: true\n")
#             if target_image:
#                 header += f"image: \"{target_image}\"\n"
#             header += (f"abstract: \"{clean_abstract}\"\n" +
#                        f"---\n\n")
            
#             md_page = header
#             if target_image and target_image != "no_event.webp":
#                 md_page += f'<img src="./{target_image}" width="300px" />\n\n'

#             # Volcar el resto de columnas como secciones Markdown
#             for key, val in row.items():
#                 if val != "" and not key.startswith('_') and key not in IGNORE_EVENT_COLUMNS and normalize_text(key) not in [normalize_text(k) for k in ['date', 'titre', 'title', 'organisateur(s)', 'descriptif', 'photo', 'image']]:
#                     md_page += f"## {key}\n\n {val}\n\n"

#             with (event_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
#                 md_file.write(md_page)


# def generate_markdown_page_card(row_dict: dict, image_filename: str, columns_to_show: list, metadata_fields: dict):
#     header = f"---\nuuid: {uuid.uuid4()}\n"
    
#     for meta_key, meta_val in metadata_fields.items():
#         if meta_key == 'tags':
#             tags_list = [t.strip() for t in str(meta_val).replace(',', ' ').split() if t.strip()]
#             formatted_tags = "[" + ", ".join([f'"{t}"' for t in tags_list]) + "]"
#             header += f"{meta_key}: {formatted_tags}\n"
#         elif meta_key == 'priority':
#             header += f"{meta_key}: {meta_val}\n"
#         else:
#             clean_meta_val = str(meta_val).replace('"', '\\"').replace('\n', ' ')
#             header += f"{meta_key}: \"{clean_meta_val}\"\n"

#     if image_filename:
#         header += f'image: "{image_filename}"\n'
    
#     header += f"---\n\n"
#     md_page = header

#     if image_filename and image_filename != "no_img_gripic.webp":
#         md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

#     for key in columns_to_show:
#         val = row_dict.get(key, "")
#         if val != "" and not key.startswith('_'):
#             md_page += f"## {key}\n\n {val}\n\n"

#     return md_page


# def csv_to_markdown_cards_or_longcards(csv_file: Path, target_dir: Path, card_type: str):
#     if not csv_file or not csv_file.exists():
#         return

#     prefix_name = "longcard" if "long" in card_type.lower() else "card"
#     default_card_img_path = IMAGES_DIR / "no_img_GRIPIC.webp"

#     with open(csv_file, mode="r", encoding="utf-8") as f:
#         reader = list(csv.DictReader(f, delimiter=";"))
#         if not reader:
#             return

#         all_columns = list(reader[0].keys())

#         # Lógica de ordenamiento por _priority
#         indexed_rows = list(enumerate(reader))

#         def sort_key(item):
#             orig_idx, row = item
#             priority_val = float('inf')
#             for col in row.keys():
#                 if col.strip().lower() in ['_priority', 'priority']:
#                     val_str = row.get(col, '').strip()
#                     if val_str:
#                         try:
#                             priority_val = int(val_str)
#                         except ValueError:
#                             priority_val = float('inf')
#                     break
            
#             sort_str = ""
#             for col in row.keys():
#                 if not col.startswith('_'):
#                     sort_str = row.get(col, '').strip()
#                     break
#             if not sort_str:
#                 for col in row.keys():
#                     if col.startswith('_') and col.strip().lower() not in ['_priority', 'priority', '_image', '_images', '_photo']:
#                         val = row.get(col, '').strip()
#                         if val:
#                             sort_str = val
#                             break

#             if priority_val != float('inf'):
#                 return (priority_val, 0, sort_str.lower(), orig_idx)
#             else:
#                 return (float('inf'), 1, "", orig_idx)

#         indexed_rows.sort(key=sort_key)
#         sorted_rows = [row for orig_idx, row in indexed_rows]

#         for idx, row in enumerate(sorted_rows, start=1):
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
#                         if clean_key == 'priority':
#                             if val:
#                                 try:
#                                     metadata_fields[clean_key] = int(val)
#                                 except ValueError:
#                                     pass
#                         elif clean_key in ['titre', 'title']:
#                             metadata_fields['title'] = val
#                             if not first_meta_val and val:
#                                 first_meta_val = clean_folder_name(val)
#                         else:
#                             metadata_fields[clean_key] = val
#                             if not first_meta_val and val:
#                                 first_meta_val = clean_folder_name(val)
#                 else:
#                     columns_to_show.append(col)

#             if first_meta_val:
#                 folder_title_part = f"{idx:02d}_{first_meta_val}"
#             else:
#                 folder_title_part = f"{idx:02d}"

#             sub_folder = target_dir / f"{prefix_name}_{folder_title_part}"
#             sub_folder.mkdir(parents=True, exist_ok=True)

#             target_image = "no_img_GRIPIC.webp"
#             source_img_path = IMAGES_DIR / img_filename if img_filename else None

#             if img_filename and source_img_path and source_img_path.exists():
#                 pure_img_name = Path(img_filename).name
#                 destination_img_path = sub_folder / pure_img_name
#                 shutil.copy(str(source_img_path), str(destination_img_path))
#                 target_image = pure_img_name
#             elif default_card_img_path.exists():
#                 shutil.copy(str(default_card_img_path), str(sub_folder / "no_img_GRIPIC.webp"))
#                 target_image = "no_img_GRIPIC.webp"

#             with (sub_folder / "index.md").open(mode="w", encoding="utf-8") as md_file:
#                 md_file.write(generate_markdown_page_card(
#                     row_dict=row,
#                     image_filename=target_image,
#                     columns_to_show=columns_to_show,
#                     metadata_fields=metadata_fields
#                 ))


# def csv_to_markdown_categories(csv_file_categories):
#     global EVENT_DIR
#     default_general_img = IMAGES_DIR / "no_img_gripic.webp"
#     default_event_img = IMAGES_DIR / "events" / "no_event.webp"
#     inputs_dir = Path("./inputs")

#     with open(csv_file_categories, newline='', encoding='utf-8') as file:
#         reader = list(csv.DictReader(file, delimiter=';'))
        
#         for idx, row in enumerate(reader, start=1):
#             group_raw = row['groupe'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
#             type_ = row['type'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip().lower()
#             name = row['nom'].replace('\n', ' ').replace('\r', ' ').replace('"', '\\"').strip()
#             description = row['description']

#             group_clean = clean_folder_name(group_raw)
#             clean_name = clean_folder_name(name)
            
#             prefix = f"{idx:02d}"
#             folder_name = f"{prefix}_{group_clean}__{type_}__{clean_name}"
#             folder_path = DATA_DIR / folder_name

#             # Detección ultra robusta sin importar tildes ni mayúsculas
#             norm_fn = normalize_text(folder_name)
#             if "evenement" in norm_fn or "agenda" in norm_fn or "calendrier" in norm_fn:
#                 EVENT_DIR = folder_path

#             folder_path.mkdir(exist_ok=True, parents=True)

#             target_image = "no_img_gripic.webp"
#             if EVENT_DIR and folder_path == EVENT_DIR and default_event_img.exists():
#                 shutil.copy(str(default_event_img), str(folder_path / "no_event.webp"))
#                 target_image = "no_event.webp"
#             elif default_general_img.exists():
#                 shutil.copy(str(default_general_img), str(folder_path / "no_img_gripic.webp"))
#                 target_image = "no_img_gripic.webp"

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

#             sub_csv = find_matching_csv(name, inputs_dir)
#             if sub_csv:
#                 csv_to_markdown_cards_or_longcards(sub_csv, folder_path, type_)


# csv_file_event = "./inputs/calendar.csv"
# csv_file_categories = "./inputs/categories.csv"

# if os.path.exists(csv_file_categories):
#     csv_to_markdown_categories(csv_file_categories)

# if os.path.exists(csv_file_event):
#     csv_to_markdown_events(csv_file_event)

# print("Folders and Markdown files created successfully with robust events handling.")


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

IGNORE_EVENT_COLUMNS = ["Sequentiel", "Séquentiel", "Contact"]
EVENT_DIR = None


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
        file_norm = normalize_text(file.stem)
        # Coincidencia flexible por si Excel corta el nombre de la pestaña por el límite de 31 caracteres
        if file_norm == target_norm or file_norm in target_norm or target_norm in file_norm:
            return file
    return None


def generate_markdown_page_card(row_dict: dict, image_filename: str, columns_to_show: list, metadata_fields: dict):
    header = f"---\nuuid: {uuid.uuid4()}\n"
    
    for meta_key, meta_val in metadata_fields.items():
        if meta_key == 'tags':
            tags_list = [t.strip() for t in str(meta_val).replace(',', ' ').split() if t.strip()]
            formatted_tags = "[" + ", ".join([f'"{t}"' for t in tags_list]) + "]"
            header += f"{meta_key}: {formatted_tags}\n"
        elif meta_key == 'priority':
            header += f"{meta_key}: {meta_val}\n"
        elif meta_key == 'event':
            # Forzar que 'event' sea booleano real (true/false sin comillas) para Gatsby
            val_bool = str(meta_val).strip().lower() in ['true', '1', 'yes', 'si', 't']
            header += f"{meta_key}: {str(val_bool).lower()}\n"
        else:
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

        # Lógica de ordenamiento por _priority
        indexed_rows = list(enumerate(reader))

        def sort_key(item):
            orig_idx, row = item
            priority_val = float('inf')
            for col in row.keys():
                if col.strip().lower() in ['_priority', 'priority']:
                    val_str = row.get(col, '').strip()
                    if val_str:
                        try:
                            priority_val = int(val_str)
                        except ValueError:
                            priority_val = float('inf')
                    break
            
            sort_str = ""
            for col in row.keys():
                if not col.startswith('_'):
                    sort_str = row.get(col, '').strip()
                    break
            if not sort_str:
                for col in row.keys():
                    if col.startswith('_') and col.strip().lower() not in ['_priority', 'priority', '_image', '_images', '_photo', '_event']:
                        val = row.get(col, '').strip()
                        if val:
                            sort_str = val
                            break

            if priority_val != float('inf'):
                return (priority_val, 0, sort_str.lower(), orig_idx)
            else:
                return (float('inf'), 1, "", orig_idx)

        indexed_rows.sort(key=sort_key)
        sorted_rows = [row for orig_idx, row in indexed_rows]

        for idx, row in enumerate(sorted_rows, start=1):
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
                        if clean_key == 'priority':
                            if val:
                                try:
                                    metadata_fields[clean_key] = int(val)
                                except ValueError:
                                    pass
                        elif clean_key in ['titre', 'title']:
                            metadata_fields['title'] = val
                            if not first_meta_val and val:
                                first_meta_val = clean_folder_name(val)
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

            folder_path.mkdir(exist_ok=True, parents=True)

            is_event_folder = "evenement" in normalize_text(folder_name)
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


csv_file_categories = "./inputs/categories.csv"

if os.path.exists(csv_file_categories):
    csv_to_markdown_categories(csv_file_categories)

print("Folders and Markdown files created successfully with robust matching.")