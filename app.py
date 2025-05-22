import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from pathlib import Path

st.title("📂 PPSC Jobs Archive Downloader")

ARCHIVE_URL = "https://ppsc.gop.pk/(S(la4uc2xgwe1vrbe1izlshhhw))/JobsArchive.aspx"
BASE_URL = "https://ppsc.gop.pk/"

@st.cache_data(show_spinner=False)
def get_file_links():
    response = requests.get(ARCHIVE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)

    file_links = []
    for link in links:
        href = link["href"]
        if any(href.lower().endswith(ext) for ext in [".pdf", ".doc", ".docx"]):
            full_url = urljoin(BASE_URL, href)
            file_links.append((link.text.strip(), full_url))
    return file_links

files = get_file_links()

if not files:
    st.warning("No downloadable files found.")
else:
    st.success(f"Found {len(files)} files.")
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)

    for name, url in files:
        filename = url.split("/")[-1]
        filepath = download_dir / filename

        if not filepath.exists():
            r = requests.get(url)
            with open(filepath, "wb") as f:
                f.write(r.content)

        with open(filepath, "rb") as f:
            st.download_button(label=f"📥 Download {filename}", data=f, file_name=filename)

    st.info("All files saved in 'downloads/' folder.")
