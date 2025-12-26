# InsightHub

InsightHub is a comprehensive "Market Research Agent" platform designed to ingest messy data (PDFs, CSVs, URLs), extract insights using AI/NLP, and generate professional scorecard reports.

Built as a Monorepo with **Next.js 14** (Frontend) and **FastAPI** (Backend).

## 🚀 Features

-   **Multi-Source Ingestion**:
    -   **URLs**: Scrapes and cleans text from web pages.
    -   **PDFs**: Extracts text from uploaded documents.
    -   **CSVs**: Parses bulk data (e.g., reviews export).
-   **Intelligent Analysis**:
    -   **Text Chunking & Cleaning**: Automatically prepares data for processing.
    -   **Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` and `pgvector` for semantic search.
    -   **Themes**: Clusters insights using K-Means to find emerging topics.
    -   **Sentiment & Claims**: Analyzes document sentiment (VADER) and detects key product claims.
-   **Interactive Dashboard**:
    -   **Brand Drilldown**: View stats, ratings trends, and top evidence for specific brands.
    -   **Visualizations**: Recharts-powered distribution and trend charts.
    -   **Evidence Viewer**: Trace insights back to the original text snippet.
-   **Configurable Scorecards**:
    -   Define factors, keywords, and weights to automatically score brands (0-100).
-   **Professional Exports**:
    -   **PowerPoint (.pptx)**: Generates a 10-slide deck with embedded charts and summaries.
    -   **CSV Zip**: Exports raw cleaned data and results.

## 🛠 Tech Stack

### Frontend (`apps/web`)
-   **Framework**: Next.js 14 (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS + Shadcn UI (Radix Primitives)
-   **State/Data**: SWR, Axios
-   **Visuals**: Recharts, Lucide Icons, TanStack Table

### Backend (`apps/api`)
-   **Framework**: FastAPI
-   **Database**: PostgreSQL 15 (with `pgvector` extension)
-   **ORM**: SQLAlchemy + Alembic (Migrations)
-   **Task Queue**: Celery + Redis
-   **ML/NLP**: `sentence-transformers`, `scikit-learn`, `nltk`
-   **Reports**: `python-pptx`, `matplotlib`

## 🏁 Getting Started

### Prerequisites
-   Docker & Docker Compose

### 1. Setup Environment
Copy the example environment files:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```
*Note: The defaults in `.env.example` work out-of-the-box with the Docker setup.*

### 2. Run with Docker
Build and start the entire stack:
```bash
docker compose up --build
```
This starts:
-   **Web App**: [http://localhost:3000](http://localhost:3000)
-   **API**: [http://localhost:8000](http://localhost:8000) (Docs at `/docs`)
-   **Postgres**: Port 5432
-   **Redis**: Port 6379
-   **Celery Worker**: Background processing

### 3. Demo Walkthrough
Follow these steps to experience the full capabilities:

1.  **Seed Data**:
    -   Go to `apps/api` in your terminal.
    -   Ensure you have a local python env or use the running container:
        ```bash
        docker compose exec api python scripts/seed_demo.py
        ```
    -   **Alternatively**: Open the Web UI, create a workspace named "Toothpaste Demo", and upload `apps/api/data/sample_reviews.csv` in the Sources tab.

2.  **Ingest**:
    -   In the **Sources** tab, make sure your sources are listed.
    -   Click **"Process All Sources"**. This triggers the background worker to chunk text, generate embeddings, and compute initial stats.

3.  **Dashboard**:
    -   Navigate to the **Dashboard**.
    -   View the "Sentiment Distribution" and "Top Claims" charts.
    -   **Drilldown**: In the "Brand Analysis" table, click on **"ShinyWhite"**.
    -   A drawer will open showing top evidence snippets. Click a snippet to see the full context modal.

4.  **Themes**:
    -   Go to the **Themes** tab to see AI-clustered topics extracted from the reviews (e.g., "Flavor/Taste", "Whitening Efficacy").

5.  **Scorecards**:
    -   Go to **Scorecards**.
    -   Create a new Scorecard (e.g., "Whitening Efficacy").
    -   Paste the default JSON config (or customize keywords).
    -   Click **Play (Run)**.
    -   View the calculated scores for each brand based on your criteria.

6.  **Export**:
    -   Go to **Exports**.
    -   Click **"Download PPTX"**.
    -   Open the generated PowerPoint file to see a professional report with native charts.

## 🧪 Testing

Run the backend test suite inside the container:
```bash
docker compose exec api pytest
```

## 📂 Project Structure

```
├── apps/
│   ├── api/                 # FastAPI Backend
│   │   ├── alembic/        # DB Migrations
│   │   ├── core/           # Config & Utils
│   │   ├── data/           # Sample Data
│   │   ├── db/             # Models & Session
│   │   ├── routers/        # API Endpoints
│   │   ├── services/       # Business Logic (Ingest, ML)
│   │   └── tests/          # Pytest Suite
│   └── web/                 # Next.js Frontend
│       ├── app/            # App Router Pages
│       ├── components/     # UI & Feature Components
│       └── lib/            # API Client
├── docker-compose.yml       # Orchestration
└── README.md                # Documentation
```
