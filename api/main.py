from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from api.rag.pdf_text import load_documents
from api.rag.retrieve_stub import EvidenceChunk, retrieve_top_k


RAW_DIR = Path("data/raw")

app = FastAPI(title="Finance RAG (Strict, Evidence-Based)")


class AskRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None
    top_k: int = 5
    max_pages: Optional[int] = None  # useful for quick dev runs


class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    score: int


class AskResponse(BaseModel):
    answer: str
    refused: bool
    refusal_reason: Optional[str] = None
    citations: List[Citation]
    evidence: List[Dict[str, Any]]  # includes chunk text for transparency


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/sources")
def sources() -> Dict[str, Any]:
    docs = load_documents(RAW_DIR, max_pages=2)  # quick listing; doesn’t need full extraction
    return {
        "raw_dir": str(RAW_DIR),
        "available_docs": [{"doc_id": d.doc_id, "filename": d.filename} for d in docs.values()],
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    docs = load_documents(RAW_DIR, max_pages=req.max_pages)
    if not docs:
        return AskResponse(
            answer="",
            refused=True,
            refusal_reason="No documents found in data/raw. Add the 10-K PDFs and try again.",
            citations=[],
            evidence=[],
        )

    # choose doc
    doc_id = req.doc_id
    if doc_id is None:
        # default to first doc
        doc_id = sorted(docs.keys())[0]

    if doc_id not in docs:
        return AskResponse(
            answer="",
            refused=True,
            refusal_reason=f"Unknown doc_id '{doc_id}'. Use /sources to see available documents.",
            citations=[],
            evidence=[],
        )

    doc = docs[doc_id]
    hits: List[EvidenceChunk] = retrieve_top_k(doc_id=doc.doc_id, doc_text=doc.text, query=req.question, top_k=req.top_k)

    if not hits:
        return AskResponse(
            answer="I can’t answer that from the indexed filing text I currently have.",
            refused=True,
            refusal_reason="No relevant evidence retrieved from the selected filing. Try rephrasing or choose a different filing.",
            citations=[],
            evidence=[],
        )

    # Strict baseline answer: don’t generate beyond evidence.
    # For now, we return a short evidence-grounded summary constructed from the top excerpts.
    answer_lines = [
        "I found relevant excerpts in the filing. Here are the most relevant sections (with citations):"
    ]
    for h in hits[:3]:
        snippet = h.text.replace("\n", " ").strip()
        snippet = snippet[:300] + ("..." if len(snippet) > 300 else "")
        answer_lines.append(f"- {snippet} [{h.chunk_id}]")

    citations = [Citation(chunk_id=h.chunk_id, doc_id=h.doc_id, score=h.score) for h in hits]

    evidence = []
    for h in hits:
        evidence.append(
            {
                "chunk_id": h.chunk_id,
                "doc_id": h.doc_id,
                "score": h.score,
                "text": h.text,
            }
        )

    return AskResponse(
        answer="\n".join(answer_lines),
        refused=False,
        refusal_reason=None,
        citations=citations,
        evidence=evidence,
    )
