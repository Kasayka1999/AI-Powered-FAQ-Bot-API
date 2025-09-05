# AI-Powered FAQ Bot API

A lightweight, AI-powered API built with FastAPI to automate responses to frequently asked questions. Designed for multi-organization use, it provides a scalable backend for intelligent FAQ bots.

---

## Project Status

This project is under active development. Status below highlights completed work, short‑term tasks, and planned RAG-related features.

### ✅ Implemented
- [x] FastAPI app scaffold and entry point
- [x] Async PostgreSQL (asyncpg) and SQLModel + Alembic
- [x] `.env` configuration with `.env.example` template
- [x] Dockerfile + docker-compose for local development
- [x] User & Organization models, JWT auth, password hashing (passlib)
- [x] AWS S3 integration (upload/list/download/delete) — utils/s3.py
- [x] Document ingestion pipeline:
  - [x] Download PDFs from S3 using boto3
  - [x] Use langchain_community.PyPDFLoader for page-level Documents
  - [x] Attach metadata (s3_key, page, source)
  - [x] Filter empty pages and chunk text with RecursiveCharacterTextSplitter (chunking complete)
- [x] PDF / Tesseract support (poppler, tesseract) and predownloaded NLTK punkt in Dockerfile
- [x] Robust loading: paginator for large S3 buckets, per-file error handling, suppression of noisy parser output

### 🚧 In progress (short-term)
- [ ] Embeddings generation pipeline (provider-agnostic)
- [ ] Persist embeddings to a vector store (pgvector on Postgres — preferred for MVP)
- [ ] RAG integration: retrieval + ranking + answer generation endpoint (`/ask`)
- [ ] Improve ingestion resilience (parallel downloads, retries, monitoring)

### 🗺️ Planned / Future work
- [ ] Expose `/ask` endpoint: context-aware answers using RAG (retrieval → generation)
- [ ] Persist and serve embeddings (pgvector with org_id tenancy and metadata; consider swapping to Qdrant for high-scale/low-latency ANN)
- [ ] Admin analytics and usage reporting: endpoints and dashboards to retrieve logs, usage metrics, interaction history, and performance KPIs (filterable by organization and time range)
- [ ] Frontend chatbot demo and example integrations
- [ ] Multi-language OCR support (Tesseract language packs + auto language detection)
- [ ] CI/CD, secrets management, and production deployment guides
- [ ] Web scraping for FAQ sources (Playwright)
  - Build and maintain Playwright-based scrapers to extract FAQ content and knowledge pages (not just PDFs).
  - Implementation notes: respect robots.txt, handle JS-rendered sites, rate limits and pagination; store raw + structured output; dedupe and normalize content before chunking/embedding.
  - Ops: add scheduler, monitoring/alerts, and a short SLA to investigate/fix scraper failures (target 2–4 hours) to keep data collection stable and accurate.


Notes
- The project follows a RAG (Retrieval-Augmented Generation) approach: page-level documents + chunking (done) → embeddings → vector search → answer generation. Page-level granularity improves retrieval relevance at the cost of more embeddings.
- Keep `.env` out of source control; use `.env.example` as the template.
---

## Getting Started

This section provides the minimal, clear steps to run the project locally for development or evaluation.

1. Create a local `.env` from the provided `.env.example` and populate values (database URL, AWS credentials, JWT secret, LLM keys). Do not commit `.env`.
2. Install dependencies (pip or Docker). For Docker development, docker-compose reads `.env`.
3. Run DB migrations:
   - alembic upgrade head
4. Start the application:
   - Local: `uvicorn app.main:app --reload`
   - Docker: `docker compose up --build` (ensure `.env` present)

Ensure `.env` contains valid credentials before running migrations. For production, use a secrets manager rather than committing secrets.

---

## Project Structure

```
.
├── migrations/           # Database migration scripts
├── app/                  # Main application source code
│   ├── api/              # API logic and routers
│   ├── database/         # DB session management
│   ├── models/           # SQLModel definitions
│   ├── services/         # Document ingestion, embeddings
│   ├── utils/            # Utilities (hashing, jwt, s3)
│   ├── config.py         # Environment-based configuration (app settings)
│   └── main.py           # FastAPI app entry point
├── Dockerfile
├── docker-compose / compose.yaml
└── README.md
```

---

## API Endpoints (Available & Planned)

Available:
- `POST /dashboard/signup` - Create a new user.
- `POST /dashboard/login` - Log in to get an access token.
- `GET /dashboard/users/me/` - Get current user's information.
- `POST /organization/create` - Create a new organization.
- `DELETE /organization/delete/` - Delete an organization.
- `POST /documents/upload` - Upload or replace a document (PDF/TXT) to S3.
- `GET /documents/my_documents` - List documents for the current organization.
- `POST /documents/download` - Download a document from S3.
- `DELETE /documents/delete` - Delete a document from S3 and database.

Planned (RAG & AI):
- `/ask` — retrieve relevant chunks and return an LLM-generated answer (RAG).
- Embeddings endpoints / background job to generate and persist embeddings.
- Vector-search endpoints for admin/debugging.
- Admin analytics and usage reporting: endpoints and dashboards for logs, usage metrics, and bot performance monitoring.

---

## MVP Summary (for reviewers / hiring managers)

Delivered:
- S3 storage + utilities, authentication, DB schemas, page-level PDF ingestion (PyPDFLoader), empty-page filtering, chunking pipeline.

Next steps to complete MVP:
- Embeddings generation (provider interface), vector store persistence, retrieval + `/ask` endpoint, minimal tests and basic monitoring.

---

## Contributing & Notes

Contributions, issues, and feature requests are welcome. See the repository issues for suggested tasks. Ensure secrets are not committed — use `.env.example` only.

## License

MIT License — see `LICENSE` for details.