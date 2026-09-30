import csv
from pathlib import Path
import os
import re
import shutil
import uuid

DATA_DIR: Path = Path("../") / "data" 
MEMBER_DIR: Path = DATA_DIR / '0_longcards_membres'
PUBLICATION_DIR: Path = DATA_DIR / "1_cards_publications"
EVENT_DIR: Path = DATA_DIR / "7_cards_événements"
FORMATION_DIR: Path = DATA_DIR / "4_longcards_formation"

SPLIT_PATTERN: str = r"\s|\'|\-|\_|«|»|,"
IMAGE_PATH = "./avatar.webp"
PUB_DEFAULT_IMAGE_PATH = "./no_img.webp"
IGNORE_MEMBER_COLUMNS = ["Nom d'utilisateur", "Prénom et Nom", "Fonction"]


def clean_folder_name(name: str) -> str:
    invalid_chars = r'<>:)([]+"/\\|?«»*'
    cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", "_", name)
    cleaned_name = re.sub(r"[^\x20-\x7E]", "", cleaned_name)
    cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
    return cleaned_name[:50].lower()


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


def make_yaml_header_member(name: str, position: str) -> str:
    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"prettyName: {''.join(re.split(pattern=SPLIT_PATTERN, string=name))}\n\n" +
            f"title: \"{name}\"\n" +
            f"abstract: \"{position}\"\n" +
            f"---\n\n")


def make_yaml_header_event(title: str, author: str, abstract: str) -> str:
    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"title: \"{title}\"\n" +
            f"author: \"{author}\"\n" +
            f"event: true\n" +
            f"abstract: \"{abstract}\"\n" +
            f"---\n\n")


def make_yaml_header_publication(pub_dict: dict) -> str:
    title = get_field(pub_dict, "Title", "title", "Titre", default="Untitled")
    authors = get_field(pub_dict, "authors", "author", "Auteurs", default="")
    pub_date = get_field(pub_dict, "date", "Date", default="")
    pub_type = get_field(pub_dict, "type", "Type", default="")
    url = get_field(pub_dict, "url", "URL", default="")
    publisher = get_field(pub_dict, "publisher", "Editeur", default="")
    container_title = get_field(pub_dict, "container_title", "container-title", default="")

    clean_title = title.replace('"', '\\"')
    clean_authors = authors.replace('"', '\\"')

    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"title: \"{clean_title}\"\n" +
            f"author: \"{clean_authors}\"\n" +
            f"authors: \"{clean_authors}\"\n" +
            f"abstract: \"{clean_authors}\"\n" +
            f"date: \"{pub_date}\"\n" +
            f"type: \"{pub_type}\"\n" +
            f"url: \"{url}\"\n" +
            f"publisher: \"{publisher}\"\n" +
            f"container_title: \"{container_title}\"\n" +
            f"publication: true\n" +
            f"---\n\n")


def make_yaml_header_formation(title: str, abstract: str, url: str = "") -> str:
    clean_title = title.replace('"', '\\"')
    clean_abstract = abstract.replace('"', '\\"')
    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"title: \"{clean_title}\"\n" +
            f"abstract: \"{clean_abstract}\"\n" +
            f"url: \"{url}\"\n" +
            f"---\n\n")


def generate_markdown_page_publication(pub_dict: dict, image_filename: str) -> str:
    md_page: str = make_yaml_header_publication(pub_dict)
    
    if image_filename:
        md_page += f'<img src="./{image_filename}" width="300px" />\n\n'

    authors = get_field(pub_dict, "authors", "author")
    pub_type = get_field(pub_dict, "type")
    publisher = get_field(pub_dict, "publisher")
    container_title = get_field(pub_dict, "container_title", "container-title")
    url = get_field(pub_dict, "url", "URL")
    abstract = get_field(pub_dict, "abstract", "resume")

    md_page += "## Informations sur la publication\n\n"
    
    if authors:
        md_page += f"- **Auteurs:** {authors}\n"
    if pub_type:
        md_page += f"- **Type de publication:** {pub_type}\n"
    if container_title:
        md_page += f"- **Revue / Conférence:** {container_title}\n"
    if publisher:
        md_page += f"- **Éditeur:** {publisher}\n"
    if url:
        md_page += f"- 🔗 **Lien HAL / Publication:** [{url}]({url})\n"
        
    md_page += "\n"

    if abstract:
        md_page += f"## Résumé\n\n{abstract}\n\n"

    return md_page


def generate_markdown_page_formation(form_dict: dict, image_filename: str) -> str:
    title = get_field(form_dict, "Title", "title", "Titre")
    description = get_field(form_dict, "Description", "description", "abstract")
    url = get_field(form_dict, "URL", "url", "Lien")

    # Transmitimos abstract="" para evitar el texto duplicado en el recuadro superior
    md_page: str = make_yaml_header_formation(title=title, abstract="", url=url)
    
    if image_filename:
        md_page += f'<img src="./{image_filename}" width="100%" />\n\n'

    if description:
        md_page += f"{description}\n\n"
        
    if url:
        md_page += f"[En savoir plus / En savoir +]({url})\n\n"

    return md_page


def generate_markdown_page_member(member_dict: dict, main_header: str, position_header: str, photo_header: str):
    md_page: str = make_yaml_header_member(
        name=member_dict[main_header], position=member_dict[position_header])
    if member_dict[photo_header] != "":
        md_page += f"![small]({member_dict[photo_header]})\n\n"
    else:
        md_page += f'<img src="{IMAGE_PATH}" width="200px" />\n\n'
    member_dict.pop(photo_header)
    for key, val in member_dict.items():
        if val != "" and key not in IGNORE_MEMBER_COLUMNS:
            md_page += f"## {key}\n\n {val}\n\n"
    return md_page


def generate_markdown_page_event(event_dict: dict, main_header: str, author_header: str, abstract_header: str, photo_header: str):
    md_page: str = make_yaml_header_event(
        title=event_dict[main_header], author=event_dict[author_header], abstract=event_dict[abstract_header])
    if event_dict[photo_header] != "":
        md_page += f"![Picture for {event_dict[main_header]}]()\n\n"
    event_dict.pop(photo_header)
    for key, val in event_dict.items():
        if val != "":
            md_page += f"## {key}\n\n {val}\n\n"
    return md_page


def csv_to_markdown_members(csv_file: str, main_header: str = "Prénom et Nom", position_header: str = "Fonction", photo_header: str = "Photo"):
    global MEMBER_DIR
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            member_name: str = row[main_header]
            member_subdir: Path = MEMBER_DIR / ("_".join(member_name.split())).lower()

            member_subdir.mkdir(parents=True, exist_ok=True)
            if row[photo_header] != '' and os.path.exists('./inputs/photos/' + row[photo_header]):
                shutil.copy('./inputs/photos/' + row[photo_header], str(member_subdir / row[photo_header]))
            else:
                shutil.copy('./resources/avatar.webp', str(member_subdir / 'avatar.webp'))
            with (member_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_member(member_dict=row,
                                                            main_header=main_header, position_header=position_header, photo_header=photo_header))


def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
    global EVENT_DIR
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            d, m, y = row['Date'].split('/')
            date_str = f'{y}-{m}-{d}'
            title: str = clean_folder_name(row[main_header])
            folder_name = date_str + "_" + title
            event_subdir: Path = EVENT_DIR / folder_name
            event_subdir.mkdir(parents=True, exist_ok=True)
            
            with (event_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_event(event_dict=row, main_header=main_header,
                              author_header=author_header, abstract_header=abstract_header, photo_header=photo_header))


def csv_to_markdown_publications(csv_file: str, photo_header: str = "Photo"):
    global PUBLICATION_DIR
    seen_titles = set()

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            title_raw = get_field(row, "Title", "title", "Titre")
            if not title_raw:
                continue

            norm_title = normalize_title(title_raw)

            if norm_title in seen_titles:
                continue
            seen_titles.add(norm_title)

            clean_title = clean_folder_name(title_raw)
            pub_date = get_field(row, "date", "Date", default="0000-00-00")
            folder_name = f"{pub_date}_{clean_title}"
            
            pub_subdir: Path = PUBLICATION_DIR / folder_name
            pub_subdir.mkdir(parents=True, exist_ok=True)

            img_filename = get_field(row, photo_header, "image", "photo", default="")
            target_image = "no_img.webp"

            if img_filename and os.path.exists(f'./inputs/public_img/{img_filename}'):
                shutil.copy(f'./inputs/public_img/{img_filename}', str(pub_subdir / img_filename))
                target_image = img_filename
            elif os.path.exists('./inputs/public_img/no_img.webp'):
                shutil.copy('./inputs/public_img/no_img.webp', str(pub_subdir / 'no_img.webp'))

            with (pub_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_publication(pub_dict=row, image_filename=target_image))


def csv_to_markdown_formations(csv_file: str, photo_header: str = "Photo"):
    global FORMATION_DIR
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            title_raw = get_field(row, "Title", "title", "Titre")
            if not title_raw:
                continue

            clean_title = clean_folder_name(title_raw)
            form_subdir: Path = FORMATION_DIR / clean_title
            form_subdir.mkdir(parents=True, exist_ok=True)

            img_filename = get_field(row, photo_header, "image", "photo", default="")
            target_image = ""

            if img_filename and os.path.exists(f'./inputs/formations_img/{img_filename}'):
                shutil.copy(f'./inputs/formations_img/{img_filename}', str(form_subdir / img_filename))
                target_image = img_filename

            # Copiar imagenes adicionales necesarias para las paginas de formación
            extra_imgs = ["nuage_1972_1999.webp", "nuage_2000_2022.webp"]
            for extra_img in extra_imgs:
                src_path = f'./inputs/formations_img/{extra_img}'
                if os.path.exists(src_path):
                    shutil.copy(src_path, str(form_subdir / extra_img))

            with (form_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_formation(form_dict=row, image_filename=target_image))


def csv_to_markdown_categories(csv_file_categories):
    with open(csv_file_categories, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        
        for row in reader:
            group = row['groupe']
            type_ = row['type']
            name = row['nom']
            description = row['description']
            
            folder_name = f"{group}_{type_}_{name}"
            folder_path = DATA_DIR / folder_name

            if "membres" in folder_name:
                global MEMBER_DIR
                MEMBER_DIR = folder_path

            if "événements" in folder_name:
                global EVENT_DIR
                EVENT_DIR = folder_path

            if "publications" in folder_name:
                global PUBLICATION_DIR
                PUBLICATION_DIR = folder_path

            if "formation" in folder_name.lower():
                global FORMATION_DIR
                FORMATION_DIR = folder_path
            
            folder_path.mkdir(exist_ok=True, parents=True)
            index_file_path = folder_path / 'index.md'
            
            with index_file_path.open(mode='w', encoding='utf-8') as index_file:
                header = f"---\n" + f"uuid: {uuid.uuid4()}\n" + f"title: \"{name.capitalize()}\"\n" + "---\n"
                content = header + description
                index_file.write(content)


# Execution pipeline
csv_file_member = './inputs/members.csv'
csv_file_event = "./inputs/calendar.csv"
csv_file_categories = "./inputs/categories.csv"
csv_file_publication = "./inputs/publications.csv"
csv_file_formation = "./inputs/formations.csv"

csv_to_markdown_categories(csv_file_categories)
csv_to_markdown_members(csv_file_member)
csv_to_markdown_events(csv_file_event)

if os.path.exists(csv_file_publication):
    csv_to_markdown_publications(csv_file_publication)

if os.path.exists(csv_file_formation):
    csv_to_markdown_formations(csv_file_formation)

print("Folders and Markdown files created successfully.")