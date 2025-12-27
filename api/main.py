from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from api.rag.faiss_store import list_sources, search


DOC_CACHE = {}

RAW_DIR = Path("data/raw")

app = FastAPI(title="Finance RAG (Strict, Evidence-Based)")


class AskRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None
    top_k: int = 5
    max_pages: Optional[int] = None


class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    score: float



class AskResponse(BaseModel):
    answer: str
    refused: bool
    refusal_reason: Optional[str] = None
    citations: List[Citation]
    evidence: List[Dict[str, Any]]  # includes chunk text for transparency

@app.get("/")
def root():
    return {"message": "Finance RAG API is running. See /docs"}

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/sources")
def sources() -> Dict[str, Any]:
    return {
        "available_docs": list_sources()
    }

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    # doc_id is optional. If provided, results filter to that filing only.
    try:
        hits = search(query=req.question, top_k=req.top_k, doc_id=req.doc_id)
    except FileNotFoundError as e:
        return AskResponse(
            answer="",
            refused=True,
            refusal_reason=str(e),
            citations=[],
            evidence=[],
        )

    if not hits:
        return AskResponse(
            answer="I can’t answer that from the indexed filings I currently have.",
            refused=True,
            refusal_reason="No relevant evidence retrieved. Try rephrasing or choose a different filing.",
            citations=[],
            evidence=[],
        )

    answer_lines = [
        "I found relevant excerpts in the filings. Here are the most relevant sections (with citations):"
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

