#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import urlparse
import shutil
import requests
from jinja2 import Environment, FileSystemLoader


PROJECT_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = PROJECT_DIR / "bin"
BUILD_DIR = PROJECT_DIR / "build"
BUILD_CSS_DIR = BUILD_DIR / "css"
BUILD_IMG_DIR = BUILD_DIR / "img"
DOWNLOADS_DIR = PROJECT_DIR / "downloads"
TEMPLATES_DIR = PROJECT_DIR / "templates"

API_FILE_PATH = Path("/home/bgutierrez/nasa.key")
API_KEY = API_FILE_PATH.read_text(encoding="utf-8").strip()

APOD_URL = "https://api.nasa.gov/planetary/apod"

# Put your bootstrap.css here if you have one
BOOTSTRAP_SOURCE = PROJECT_DIR / "bootstrap.css"


def clean_build():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    if DOWNLOADS_DIR.exists():
        shutil.rmtree(DOWNLOADS_DIR)

    BUILD_CSS_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_IMG_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def copy_css():
    if BOOTSTRAP_SOURCE.exists():
        shutil.copy2(BOOTSTRAP_SOURCE, BUILD_CSS_DIR / "bootstrap.css")


def get_three_apod_entries():
    entries = []
    seen_dates = set()

    while len(entries) < 3:
        response = requests.get(
            APOD_URL,
            params={
                "api_key": API_KEY,
                "count": 5
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        for item in data:
            if item.get("media_type") != "image":
                continue

            image_url = item.get("hdurl") or item.get("url")
            if not image_url:
                continue

            date = item.get("date", "")
            if date in seen_dates:
                continue

            image_name = Path(urlparse(image_url).path).name

            entry = {
                "author": item.get("copyright", "Not listed"),
                "date": date,
                "image_name": image_name,
                "title": item.get("title", ""),
                "explanation": item.get("explanation", ""),
                "image_url": image_url
            }

            entries.append(entry)
            seen_dates.add(date)

            if len(entries) == 3:
                break

    return entries


def download_images(entries):
    for entry in entries:
        image_response = requests.get(entry["image_url"], timeout=30)
        image_response.raise_for_status()

        download_path = DOWNLOADS_DIR / entry["image_name"]
        download_path.write_bytes(image_response.content)


def copy_images_to_build(entries):
    for entry in entries:
        src = DOWNLOADS_DIR / entry["image_name"]
        dst = BUILD_IMG_DIR / entry["image_name"]
        shutil.copy2(src, dst)


def make_render_data(entries):
    render_entries = []

    for entry in entries:
        render_entries.append({
            "author": entry["author"],
            "date": entry["date"],
            "image_name": entry["image_name"],
            "title": entry["title"],
            "explanation": entry["explanation"]
        })

    return render_entries


def render_newsletter(entries):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("newsletter.html.j2")
    rendered_html = template.render(entries=entries)

    output_file = BUILD_DIR / "newsletter.html"
    output_file.write_text(rendered_html, encoding="utf-8")


def main():
    clean_build()
    copy_css()

    apod_entries = get_three_apod_entries()
    download_images(apod_entries)
    copy_images_to_build(apod_entries)

    render_entries = make_render_data(apod_entries)
    render_newsletter(render_entries)

    print("Done.")
    print(f"Open: {BUILD_DIR / 'newsletter.html'}")


if __name__ == "__main__":
    main()
