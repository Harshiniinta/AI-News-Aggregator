# ⚡ Autonomous AI News Intelligence & Multi-Agent Curation Pipeline

An automated, end-to-end multi-agent ETL system that ingests multimodal AI news across **YouTube, OpenAI, and Anthropic**, transcribes spoken video dialogue, synthesizes structured technical digests, and delivers personalized intelligence briefings through a **Streamlit Web Dashboard** and **automated morning email newsletters**.

---

## 🌟 Key Highlights

- **Multimodal Video Ingestion**: Uses `youtube-transcript-api` to pull 15,000+ token closed-caption transcripts from top AI channels, transforming spoken video into searchable, indexable text.
- **Document Normalization**: Uses IBM's **Docling** and feed parsers to convert unstructured web articles into clean, fluff-free Markdown.
- **Multi-Agent Hierarchy (Pydantic Structured Outputs)**:
  - **`DigestAgent`**: Summarizes long-form text and transcripts into 3 core technical takeaways (*Key Insight*, *Developer Impact*, *Actionable Takeaway*) using `gpt-4o-mini`.
  - **`CuratorAgent`**: Evaluates digests against custom user personas (interests, expertise levels) and ranks candidates on a **0.0–10.0 scale** using `gpt-4.1`.
  - **`EmailAgent`**: Synthesizes editorial introductions and previews for the daily morning briefing.
- **Interactive Streamlit Web Hub**: A real-time UI to monitor ingested database lakes, tune persona weights, view responsive newsletter previews, and dispatch digests on-demand.
- **Card-Styled Email Delivery**: Mobile-responsive HTML template featuring color-coded source badges (`🔴 YouTube`, `🟢 OpenAI`, `🟣 Anthropic`), relevance scores, and embedded YouTube thumbnails delivered via Gmail SMTP.
- **Production Architecture**: Containerized PostgreSQL database running on Docker with SQLAlchemy ORM and schema de-duplication.

---

## 🏗️ Architecture & Pipeline Flow

```
1. MULTIMODAL INGESTION
   ├── YouTube RSS ────────► youtube-transcript-api (Extracts Audio Transcripts)
   ├── OpenAI Research RSS ─► FeedParser / Trafilatura
   └── Anthropic Blog RSS ──► Docling Converter (Converts HTML to Markdown)
                                  │
                                  ▼
2. DATABASE STORAGE (PostgreSQL 17 on Docker)
   ├── youtube_videos
   ├── openai_articles
   ├── anthropic_articles
   └── digests
                                  │
                                  ▼
3. MULTI-AGENT INTELLIGENCE LAYER
   ├── DigestAgent   ──► Structured 3-Bullet Technical Summaries (gpt-4o-mini)
   ├── CuratorAgent  ──► User Persona Scoring (0.0 to 10.0) & Ranking (gpt-4.1)
   └── EmailAgent    ──► Editorial Synthesis & Contextual Greetings
                                  │
                                  ▼
4. DUAL PRESENTATION & DELIVERY
   ├── Streamlit Web UI (http://localhost:8501)
   └── Automated SMTP Dispatch (Mobile-Responsive HTML Newsletter)
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.12+ (or [uv](https://docs.astral.sh/uv/))
- Docker & Docker Compose

### 2. Clone and Install Dependencies
```bash
git clone https://github.com/Harshiniinta/AI-News-Aggregator.git
cd AI-News-Aggregator
uv sync
```

### 3. Start PostgreSQL Database
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 4. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
MY_EMAIL=your_email@gmail.com
APP_PASSWORD=your_16_character_google_app_password

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ai_news_aggregator
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## 💻 Running the Application

### Launch the Streamlit Intelligence Dashboard
```bash
./.venv/bin/streamlit run app/dashboard.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser to explore the curated feed, inspect the ingestion lake, and dispatch digests to your inbox with a single click.

### Run the Full Daily Pipeline via CLI
```bash
./.venv/bin/python main.py
```
*(Optionally specify lookback hours and top article count: `./.venv/bin/python main.py 48 5`)*

### Run Individual Micro-Services
```bash
# Run Feed Scrapers
./.venv/bin/python app/runner.py

# Extract YouTube Transcripts
./.venv/bin/python app/services/process_youtube.py

# Convert Anthropic Webpages to Markdown
./.venv/bin/python app/services/process_anthropic.py

# Run AI Digest Agent
./.venv/bin/python app/services/process_digest.py

# Run AI Curator & Persona Ranking
./.venv/bin/python app/services/process_curator.py
```

---

## 🛠️ Tech Stack

- **Language**: Python 3.12+
- **Database & Infrastructure**: PostgreSQL 17, Docker, Docker Compose, SQLAlchemy
- **AI & Agents**: OpenAI API (`gpt-4o-mini`, `gpt-4.1`), Pydantic Structured Outputs
- **Ingestion & Parsing**: `youtube-transcript-api`, Docling (`docling`), `feedparser`, `beautifulsoup4`, `markdown`
- **Frontend & Presentation**: Streamlit, Custom Responsive HTML/CSS Email Template
- **Delivery**: Python `smtplib` (Gmail SMTP with App Password)
