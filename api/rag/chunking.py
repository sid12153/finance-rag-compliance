# api/rag/chunking.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import re


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    filename: str
    company: str
    filing_year: str
    filing_type: str
    text: str
    n_chars: int


def clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def chunk_document_text(
    doc_text: str,
    doc_id: str,
    filename: str,
    company: str,
    filing_year: str,
    filing_type: str,
    chunk_chars: int = 1400,
    overlap_chars: int = 200,
) -> List[Chunk]:
    """
    Character-based chunking with overlap. Deterministic chunk IDs.
    """
    text = clean_text(doc_text)
    if not text:
        return []

    chunks: List[Chunk] = []
    i = 0
    n = len(text)
    k = 0

    while i < n:
        j = min(i + chunk_chars, n)
        chunk_text = text[i:j].strip()

        chunk_id = f"{doc_id}::chunk_{k}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                filename=filename,
                company=company,
                filing_year=filing_year,
                filing_type=filing_type,
                text=chunk_text,
                n_chars=len(chunk_text),
            )
        )

        k += 1
        if j == n:
            break
        i = max(0, j - overlap_chars)

    return chunks
