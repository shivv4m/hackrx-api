import os
import requests
import pdfplumber
import docx2txt
import tempfile
import mimetypes
import email
from bs4 import BeautifulSoup

def download_file_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    suffix = mimetypes.guess_extension(response.headers.get('Content-Type', 'application/octet-stream'))
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def extract_text_from_docx(file_path: str) -> str:
    return docx2txt.process(file_path)

def extract_text_from_eml(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        msg = email.message_from_file(f)
    parts = []
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            parts.append(part.get_payload(decode=True).decode(errors="ignore"))
        elif part.get_content_type() == "text/html":
            html = part.get_payload(decode=True).decode(errors="ignore")
            text = BeautifulSoup(html, "html.parser").get_text()
            parts.append(text)
    return "\n".join(parts)

def extract_text_from_document(doc_url: str) -> str:
    file_path = download_file_from_url(doc_url)

    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            mime_type = mime_type.lower()

        if mime_type == "application/pdf":
            return extract_text_from_pdf(file_path)
        elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return extract_text_from_docx(file_path)
        elif mime_type == "message/rfc822" or file_path.endswith(".eml"):
            return extract_text_from_eml(file_path)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")
    finally:
        os.remove(file_path)

