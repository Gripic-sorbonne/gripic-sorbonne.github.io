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


def find_matching_csv(submenu_name: str, inputs_dir: Path) -> Path:
    target_norm = normalize_text(submenu_name)
    if not inputs_dir.exists():
        return None
        
    for file in inputs_dir.glob("*.csv"):
        file_norm = normalize_text(file.stem)
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
            val_bool = str(meta_val).strip().lower() in ['true', '1', 'yes', 'si', 't']
            header += f"{meta_key}: {str(val_bool).lower()}\n"
        elif meta_key == 'date':
            clean_date = str(meta_val).strip().replace('/', '-')
            header += f"{meta_key}: \"{clean_date}\"\n"
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
            date_str = ""

            for col in all_columns:
                val = row.get(col, "").strip()
                clean_col = col.lstrip('_').lower()
                
                if clean_col in ['image', 'images', 'photo']:
                    if val:
                        img_filename = val
                elif clean_col in ['date']:
                    if val:
                        d_val = val.replace('/', '-')
                        parts = d_val.split('-')
                        if len(parts) == 3:
                            if len(parts[0]) == 2:  # DD-MM-YYYY
                                d, m, y = parts
                                date_str = f"{y}-{m}-{d}"
                            else:  # YYYY-MM-DD
                                y, m, d = parts
                                date_str = f"{y}-{m}-{d}"
                        else:
                            date_str = val
                        metadata_fields['date'] = date_str
                        if 'year' not in metadata_fields and len(date_str) >= 4:
                            metadata_fields['year'] = date_str[:4]
                elif clean_col in ['year']:
                    if val:
                        metadata_fields['year'] = val
                elif clean_col in ['event']:
                    if val:
                        metadata_fields['event'] = val
                elif col.startswith('_'):
                    if clean_col == 'priority':
                        if val:
                            try:
                                metadata_fields[clean_col] = int(val)
                            except ValueError:
                                pass
                    elif clean_col in ['titre', 'title']:
                        metadata_fields['title'] = val
                        if not first_meta_val and val:
                            first_meta_val = clean_folder_name(val)
                    else:
                        metadata_fields[clean_col] = val
                        if not first_meta_val and val:
                            first_meta_val = clean_folder_name(val)
                else:
                    columns_to_show.append(col)

            if first_meta_val:
                folder_title_part = f"{idx:02d}_{first_meta_val}"
            else:
                folder_title_part = f"{idx:02d}"

            # CLAVE: Anteponer la fecha al nombre de la carpeta para que gatsby-node.js asigne fields.date
            if date_str:
                folder_name = f"{date_str}_{prefix_name}_{folder_title_part}"
            else:
                folder_name = f"{prefix_name}_{folder_title_part}"

            sub_folder = target_dir / folder_name
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

print("Folders and Markdown files created successfully with date prefixing for Gatsby.")