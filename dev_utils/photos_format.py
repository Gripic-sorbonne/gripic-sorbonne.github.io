from pathlib import Path
from PIL import Image

# Source folder
PHOTOS_DIR = Path("./photos")

# Destination folder for the converted images
OUTPUT_DIR = Path("./form_photos")

# Supported image formats
EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".PNG", ".JPEG"}


def convert_images_to_webp(src_dir: Path, dest_dir: Path):
    if not src_dir.exists():
        print(f"Error: The source folder {src_dir} does not exist.")
        return

    # Create the destination folder if it does not exist
    dest_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for file_path in src_dir.iterdir():
        if file_path.suffix in EXTENSIONS:
            # Build the destination path, keeping the filename but changing the extension to .webp
            webp_path = dest_dir / f"{file_path.stem}.webp"

            try:
                with Image.open(file_path) as img:
                    # Convert the color mode to RGB if necessary to avoid errors when saving as WEBP
                    if img.mode in ("RGBA", "P") and file_path.suffix.lower() in (".jpg", ".jpeg"):
                        img = img.convert("RGB")

                    img.save(webp_path, "WEBP", quality=80)
                    print(f"Converted and saved: {file_path.name} -> {webp_path}")
                    count += 1

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

    print(f"\nProcess completed! {count} images were saved in the '{dest_dir.name}' folder.")


if __name__ == "__main__":
    convert_images_to_webp(PHOTOS_DIR, OUTPUT_DIR)