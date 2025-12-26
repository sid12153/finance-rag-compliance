# Architecture

This project implements a strict evidence-first retrieval workflow for analyst-style risk and disclosure analysis of SEC 10-K filings.

Core rule:
**Every response must be grounded in retrieved excerpts from indexed filings and must include citations.**
If the system cannot retrieve relevant evidence, it must refuse.

---

## System Components

### 1) Document Ingestion (PDF → Text)
- Input: SEC 10-K filings in PDF format stored in `data/raw`
- Extraction: `pdfplumber`
- Output: raw text per filing (document-level)

### 2) Chunking (Text → Overlapping Segments)
- Filing text is cleaned and split into overlapping character chunks.
- Each chunk stores:
  - `chunk_id` (deterministic)
  - `doc_id` and filename
  - company, filing year, filing type
  - chunk text and length
- Output: `data/processed/chunks.jsonl`

### 3) Embeddings (Chunks → Vectors)
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embeddings are normalized for cosine similarity retrieval.
- Output: vectors aligned 1:1 with chunk metadata.

### 4) Vector Store (FAISS Index)
- Index type: `IndexFlatIP` (inner product on normalized embeddings = cosine similarity)
- Artifacts:
  - `data/processed/embeddings.faiss`
  - `data/processed/embeddings_meta.jsonl` (metadata aligned to FAISS ids)

### 5) Retrieval (Question → Top-k Evidence)
Given a user question:
- embed query using the same embedding model
- retrieve top-k chunk IDs from FAISS
- optionally filter by company / year (UI selection)
- return top chunks with scores and citations

### 6) API + UI Layer
- FastAPI backend:
  - `/sources` lists available filings
  - `/ask` performs retrieval and returns evidence + citations
  - `/health` health check
- Streamlit UI:
  - company selection
  - question input
  - answer panel + citations
  - evidence excerpts display

---

## Data Flow Summary

1. PDFs → extracted text  
2. Text → chunked JSONL  
3. JSONL → embeddings  
4. embeddings → FAISS index  
5. question → retrieve top chunks  
6. return evidence + citations (strict)

---

## Guardrails (Planned, Day 11)
Guardrails will enforce:
- scope restriction (no external knowledge)
- minimum retrieval confidence thresholds
- refusal behavior when evidence is insufficient
- citation formatting consistency

Optional later: a synthesis step that summarizes retrieved evidence while preserving strict citations.
