import os
import re
import time
import json
import urllib3
import requests
from bs4 import BeautifulSoup

# Disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://kit-117.sorbonne-universite.fr"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CACHE_DIR = "cache_html"
PHOTOS_DIR = "photos"
DATASET_FILE = "members_dataset.json"
DEFAULT_PLACEHOLDER = "s-de-sorbonne.png"


def download_profile_picture(img_url: str, slug: str) -> str:
    """Downloads the profile picture if present, returning its local relative path."""
    if not img_url:
        return None

    if not img_url.startswith("http"):
        img_url = f"{BASE_URL}{img_url}"

    file_ext = os.path.splitext(img_url)[-1].split("?")[0]
    if not file_ext or len(file_ext) > 5:
        file_ext = ".jpg"

    formatted_filename = f"{slug.replace('-', '_')}{file_ext}"
    photo_path = os.path.join(PHOTOS_DIR, formatted_filename)

    if os.path.exists(photo_path):
        return photo_path

    try:
        res = requests.get(img_url, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            with open(photo_path, "wb") as f:
                f.write(res.content)
            return photo_path
    except Exception as e:
        print(f"  -> Failed to download image for {slug}: {e}")

    return None


def parse_member_html(html_content: bytes, slug: str) -> dict:
    """Parses raw HTML bytes, extracting structured fields and downloading photo if available."""
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Full Name: Seleccionar el h1 de la sección headline__content para evitar el h1 del header global
    name_elem = soup.select_one(".headline__content h1.headline__title")
    full_name = name_elem.get_text(strip=True) if name_elem else None

    # 2. Role / Title: Combina el cargo principal (p.color-dark) y la categoría de miembro si existen
    role_parts = []
    headline_content = soup.select_one(".headline__content")
    if headline_content:
        # Cargo principal (ej. "Doctorante-chercheuse")
        title_elem = headline_content.select_one("p.color-dark")
        if title_elem:
            role_parts.append(title_elem.get_text(strip=True))
        
        # Categoría (ej. "Membre permanent en formation doctorale")
        # Se buscan <p> hijos directos de .headline__content que no sean el cargo principal ni estén vacíos
        for p in headline_content.find_all("p", recursive=False):
            if "color-dark" not in p.get("class", []) and p.get_text(strip=True):
                role_parts.append(p.get_text(strip=True))
                
    role = " | ".join(role_parts) if role_parts else None

    # 3. Profile Picture
    photo_local_path = None
    profile_img = soup.select_one(".headline__portrait img, .field--name-user-picture img, .profile img")

    if profile_img:
        img_src = profile_img.get("src") or profile_img.get("data-src")
        img_title = profile_img.get("title", "")

        if img_src and DEFAULT_PLACEHOLDER not in img_src and img_title != "Persona sans photo":
            photo_local_path = download_profile_picture(img_src, slug)
    else:
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img and og_img.get("content"):
            img_src = og_img["content"]
            if DEFAULT_PLACEHOLDER not in img_src:
                photo_local_path = download_profile_picture(img_src, slug)

    return {
        "slug": slug,
        "full_name": full_name,
        "role": role,
        "photo_path": photo_local_path,
    }


def process_members(max_pages: int = 15):
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    all_members_data = []

    for page in range(max_pages):
        page_url = f"{BASE_URL}/membres?page={page}"
        print(f"\n--- Processing Directory Page {page}: {page_url} ---")

        try:
            res = requests.get(page_url, headers=HEADERS, verify=False, timeout=10)
            soup = BeautifulSoup(res.content, "html.parser")
            member_links = soup.select("h3 a")
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            continue

        if not member_links:
            print(f"No members found on page {page}. Stopping execution.")
            break

        for a_tag in member_links:
            relative_path = a_tag["href"]
            slug = relative_path.split("/")[-1]
            filepath = os.path.join(CACHE_DIR, f"{slug}.html")
            perfil_url = f"{BASE_URL}{relative_path}"

            # Step A: Cache raw HTML or download if missing
            if os.path.exists(filepath):
                print(f"[Cache Hit] Reading raw HTML for {slug}...")
                with open(filepath, "rb") as f:
                    html_content = f.read()
            else:
                print(f"[Downloading] Raw HTML for {slug}...")
                try:
                    res_perfil = requests.get(perfil_url, headers=HEADERS, verify=False, timeout=10)
                    if res_perfil.status_code == 200:
                        html_content = res_perfil.content
                        with open(filepath, "wb") as f:
                            f.write(html_content)
                        time.sleep(0.3)
                    else:
                        print(f"  -> HTTP Error {res_perfil.status_code} on {perfil_url}")
                        continue
                except Exception as e:
                    print(f"  -> Connection failure on {perfil_url}: {e}")
                    continue

            # Step B: Parse extracted raw HTML
            member_data = parse_member_html(html_content, slug)
            all_members_data.append(member_data)

    # Step C: Save structured JSON dataset
    with open(DATASET_FILE, "w", encoding="utf-8") as f:
        json.dump(all_members_data, f, ensure_ascii=False, indent=2)

    print(f"\nComplete! Extracted {len(all_members_data)} records to '{DATASET_FILE}'.")


if __name__ == "__main__":
    process_members()