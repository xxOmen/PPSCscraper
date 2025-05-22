import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import zipfile
import io

st.title("📄 Download PPSC Archive PDFs as ZIP")

ARCHIVE_URL = "https://ppsc.gop.pk/(S(la4uc2xgwe1vrbe1izlshhhw))/JobsArchive.aspx"
BASE_URL = "https://ppsc.gop.pk/"

@st.cache_data(show_spinner=False)
def get_pdf_links():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(ARCHIVE_URL, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)

    pdf_links = []
    for link in links:
        href = link["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            filename = full_url.split("/")[-1]
            pdf_links.append((filename, full_url))
    return pdf_links

pdf_files = get_pdf_links()

if not pdf_files:
    st.warning("No PDF files found.")
else:
    st.success(f"Found {len(pdf_files)} PDF files.")

    # ZIP buffer for all PDF files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, url in pdf_files:
            try:
                file_resp = requests.get(url, timeout=15)
                file_resp.raise_for_status()
                zipf.writestr(filename, file_resp.content)
            except Exception as e:
                st.warning(f"Skipped {filename}: {e}")

    zip_buffer.seek(0)

    st.download_button(
        label="📦 Download All PDFs as ZIP",
        data=zip_buffer,
        file_name="PPSC_PDF_Archive.zip",
        mime="application/zip"
    )
