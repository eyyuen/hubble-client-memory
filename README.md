# Hubble Client Memory System

An AI-powered client knowledge base built for the Hubble Systems Challenge (Stage 3).
Eliminates the founder bottleneck by making every client preference, brand guideline,
and past feedback instantly accessible to the whole team.

## Demo Video
[Watch Demo Video](your-loom-link-here)

## The Problem
At Hubble, client knowledge is scattered across:
- WhatsApp messages
- Emails
- Meeting notes
- Verbal instructions from the founder

Nobody consolidates this — so knowledge lives in people's heads.
New team members don't know client preferences. The founder becomes
a bottleneck for every creative decision.

## The Solution
A two-part system:

**Part 1: Knowledge Ingestion**
Paste any raw text (WhatsApp, email, meeting notes) →
Claude extracts structured preferences automatically →
Stored in ChromaDB vector database

**Part 2: Instant Retrieval**
Team member asks any question in plain English →
System searches all stored client knowledge →
Claude answers with specific, actionable details →
Sources shown so team knows where info came from

## Features
- **Multi-source ingestion** — WhatsApp, email, meeting notes, briefs
- **Claude AI extraction** — automatically identifies preferences, brand guidelines, common revisions, communication style
- **ChromaDB vector search** — semantic search finds relevant context even when exact words don't match
- **Client filtering** — search all clients or filter by specific client
- **Source tracking** — every answer shows which document it came from
- **Sample data included** — 4 pre-loaded clients to demo instantly

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI processing | Anthropic Claude API (claude-sonnet-4-6) |
| Vector database | ChromaDB |
| Embeddings | sentence-transformers |
| Frontend | Streamlit |
| Language | Python 3.9+ |

## Getting Started

### Prerequisites
- Python 3.9+
- Anthropic API key — [console.anthropic.com](https://console.anthropic.com)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/eyyuen/hubble-client-memory.git
cd hubble-client-memory
```

**2. Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install streamlit anthropic chromadb python-dotenv sentence-transformers
```

**4. Set up environment variables**

Create a `.env` file:
ANTHROPIC_API_KEY=your-anthropic-api-key

**5. Run the app**
```bash
streamlit run app.py
```

Open `http://localhost:8501`

**6. Load sample data**

Click **"Load sample clients"** in the sidebar to populate with 4 demo clients:
- Bloom Studio
- Nomad Collective
- TechVentures SG
- Casa Living

## How It Works
Raw text input (any source)
↓
Claude extracts:

Preferences
Brand guidelines
Communication style
Common revisions
Key contacts
↓
Stored in ChromaDB with metadata
↓
Team asks question in plain English
↓
ChromaDB semantic search finds relevant context
↓
Claude generates specific, actionable answer
↓
Sources displayed for transparency

## What's Next
- WhatsApp direct integration via Twilio — auto-ingest messages without copy-paste
- Gmail integration — automatically extract preferences from email threads
- Slack integration — team can query client memory directly from Slack
- Notion/Google Docs sync — pull from existing documentation
- Client profile dashboard — visual overview of each client

## Project Structure
hubble-client-memory/
├── app.py            # Main Streamlit app
├── .env.example      # Environment variables template
├── .gitignore
└── README.md

## Built By
Yuen Wei Ling — [github.com/eyyuen](https://github.com/eyyuen)

Submitted for the Hubble Systems Challenge Stage 3 · July 2026
