import csv
import re
import ssl
import urllib.request
from bs4 import BeautifulSoup
from bs4.element import Tag


Base_URL = "https://www.gripic.fr/page/programmes-prives"


def extract_pure_text_perfect(url, output_filename = "result.txt"):

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context = ctx) as resp:
        html = resp.read().decode("utf-8")

    soup = BeautifulSoup (html, "lxml")

    unwanted_tags = ["script", "style", "link", "meta", "noscript"]
    for tag in soup(unwanted_tags):
        if isinstance(tag, Tag):
            tag.decompose()

    pure_text = soup.get_text()

    lines = (line.strip() for line in pure_text.splitlines())
    clean_text = "\n".join(line for line in lines if line)

    output_filename = "/Users/jungmin/Desktop/gripic_sorbonne/gripic-sorbonne.github.io/scripts/inputs/result1.txt"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(clean_text)
    print("Extracted text saved to", output_filename)


extract_pure_text_perfect(Base_URL, "result1.txt")