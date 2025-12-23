from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pdfplumber


@dataclass
class Document:
    doc_id: str
    filename: str
    text: str


def list_pdfs(raw_dir: Path) -> List[Path]:
    if not raw_dir.exists():
        return []
    return sorted([p for p in raw_dir.iterdir() if p.suffix.lower() == ".pdf"])


def extract_pdf_text(pdf_path: Path, max_pages: int | None = None) -> str:
    pages_text: List[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        n_pages = len(pdf.pages)
        limit = n_pages if max_pages is None else min(n_pages, max_pages)

        for i in range(limit):
            page = pdf.pages[i]
            txt = page.extract_text() or ""
            txt = txt.strip()
            if txt:
                pages_text.append(txt)

    return "\n\n".join(pages_text)


def load_documents(raw_dir: Path, max_pages: int | None = None) -> Dict[str, Document]:
    docs: Dict[str, Document] = {}
    for pdf_path in list_pdfs(raw_dir):
        doc_id = pdf_path.stem
        text = extract_pdf_text(pdf_path, max_pages=max_pages)
        docs[doc_id] = Document(doc_id=doc_id, filename=pdf_path.name, text=text)
    return docs
