# Finance RAG API (FastAPI)

This folder contains the backend service for the Finance RAG project.

The API is responsible for:
- ingesting and indexing a small set of SEC 10-K filings (selected companies and years)
- retrieving the most relevant filing excerpts for a user question
- generating answers with citations back to the original filing text
- applying basic guardrails (scope limits, refusal when evidence is missing, and citation requirements)

## Planned Endpoints

- `GET /health`  
  Simple health check.

- `POST /ask`  
  Takes a user question and optional filters (company, year) and returns:
  - answer
  - citations (chunk IDs + source metadata)
  - retrieved excerpts (for transparency)

- `GET /sources`  
  Lists available companies, years, and filing metadata currently indexed.

## How it will work (high level)

1. Load filing text and split into chunks  
2. Embed chunks and store them in a local vector index  
3. Retrieve top-k chunks for each question  
4. Generate an answer grounded in retrieved chunks  
5. Return citations and excerpts along with the answer

## Notes

This is intentionally kept lightweight and reproducible:
- local vector index (no paid infra)
- small, curated set of filings for a high-quality demo
- emphasis on correctness, citations, and evaluation over UI polish
