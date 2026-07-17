from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import anthropic
import chromadb
import json
import re
import os
from datetime import datetime

# ── Clients ─────────────────────────────────────────────────
client = anthropic.Anthropic()
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("client_memory")

st.set_page_config(
    page_title="Hubble Client Memory",
    layout="wide"
)

# ── CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 15px; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    .stApp { background: #f8f9fb; }

    .top-header {
        background: #0f0f0e;
        color: white;
        padding: 18px 28px;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .logo {
        width: 34px; height: 34px;
        background: #e8a020;
        border-radius: 6px;
        display: flex; align-items: center;
        justify-content: center;
        font-weight: 700; font-size: 13px;
        color: #0f0f0e; flex-shrink: 0;
    }
    .brand { font-size: 0.95rem; font-weight: 600; }
    .brand-sub { font-size: 0.68rem; color: rgba(255,255,255,0.45); margin-top:1px; }

    .card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 14px;
    }
    .card-label {
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 8px;
    }
    .source-tag {
        display: inline-block;
        background: #f1f5f9;
        border: 0.5px solid #e2e8f0;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.7rem;
        color: #64748b;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .answer-box {
        background: #f8faff;
        border-left: 3px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        font-size: 0.9rem;
        color: #1e293b;
        line-height: 1.75;
    }
    .empty-state {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 48px;
        text-align: center;
        color: #94a3b8;
    }
    .stTextArea textarea {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        line-height: 1.6 !important;
    }
    .stTextInput > div > div > input {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        font-size: 0.88rem !important;
    }
    .stSelectbox > div > div {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
    }
    .stButton > button {
        background: #0f0f0e !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #1a1a18 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 18rem !important;
        min-width: 18rem !important;
        transform: none !important;
        background: #0f0f0e !important;
    }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.78rem !important;
    }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { 
        display: block !important;
        width: 18rem !important;
        min-width: 18rem !important;
    }
</style>
""", unsafe_allow_html=True)

    

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <div class="logo">H</div>
    <div>
        <div class="brand">Hubble Collective</div>
        <div class="brand-sub">Client Memory System</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────
def extract_preferences(raw_text: str, client_name: str, source: str) -> dict:
    """Use Claude to extract structured preferences from raw text."""
    prompt = f"""
You are an operations assistant at Hubble Collective, a creative agency.

Extract client preferences and important notes from this raw text.
Client: {client_name}
Source: {source}
Raw text: {raw_text}

Return ONLY a JSON object:
{{
    "preferences": ["preference 1", "preference 2"],
    "brand_guidelines": ["guideline 1", "guideline 2"],
    "communication_style": "description of how they communicate",
    "common_revisions": ["common revision 1", "common revision 2"],
    "key_contacts": ["contact info if mentioned"],
    "summary": "2-sentence summary of what was learned about this client"
}}

Extract only what's actually mentioned. Leave arrays empty if not mentioned.
Return ONLY the JSON.
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def store_in_chromadb(client_name: str, source: str,
                       raw_text: str, extracted: dict):
    """Store extracted knowledge in ChromaDB."""
    doc_id = f"{client_name}_{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    doc_id = re.sub(r"[^a-zA-Z0-9_-]", "_", doc_id)

    document = f"""
Client: {client_name}
Source: {source}
Summary: {extracted.get('summary', '')}
Preferences: {', '.join(extracted.get('preferences', []))}
Brand Guidelines: {', '.join(extracted.get('brand_guidelines', []))}
Communication Style: {extracted.get('communication_style', '')}
Common Revisions: {', '.join(extracted.get('common_revisions', []))}
Raw Notes: {raw_text}
"""
    collection.add(
        documents=[document],
        metadatas=[{
            "client": client_name,
            "source": source,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }],
        ids=[doc_id]
    )


def query_client_memory(question: str, client_name: str = None) -> dict:
    """Query ChromaDB and use Claude to answer."""
    where = {"client": client_name} if client_name and client_name != "All clients" else None

    results = collection.query(
        query_texts=[question],
        n_results=min(5, collection.count()) if collection.count() > 0 else 1,
        where=where
    )

    if not results["documents"][0]:
        return {
            "answer": "No client information found. Add some client knowledge first.",
            "sources": []
        }

    context = "\n\n---\n\n".join(results["documents"][0])
    metadatas = results["metadatas"][0]

    prompt = f"""
You are an operations assistant at Hubble Collective.
Answer this question using the client knowledge below.
Be specific and practical. If the answer isn't in the knowledge base, say so.

Question: {question}

Client Knowledge:
{context}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    sources = [
        f"{m.get('client')} — {m.get('source')} ({m.get('added_at')})"
        for m in metadatas
    ]

    return {
        "answer": response.content[0].text.strip(),
        "sources": sources
    }


def get_all_clients():
    """Get list of unique clients in the database."""
    if collection.count() == 0:
        return []
    results = collection.get()
    clients = list(set([m["client"] for m in results["metadatas"]]))
    return sorted(clients)


def seed_sample_data():
    """Seed sample client data for demo purposes."""
    samples = [
        {
            "client": "Bloom Studio",
            "source": "WhatsApp",
            "text": "Hey just a reminder we always use British English for all our content. No Americanisms please. Also our brand colours are sage green and warm white only. We hate stock photos — everything must be original photography. Our founder Sarah prefers minimal text on visuals, let the imagery speak."
        },
        {
            "client": "Bloom Studio",
            "source": "Meeting Notes",
            "text": "Meeting 12 June — Sarah confirmed they want all videos under 60 seconds for Instagram. Longer form content (3-5 min) only for YouTube. They prefer candid behind-the-scenes shots over polished product shots. Tone should be warm and conversational, never corporate."
        },
        {
            "client": "Nomad Collective",
            "source": "Email",
            "text": "Hi team, just to confirm our brand guidelines — we are all about raw authentic storytelling. No filters, no heavy editing. We want our audience to feel like they are right there with us. Captions should be casual and conversational. We use lowercase for all social captions. Our target audience is 25-35 adventure travelers."
        },
        {
            "client": "Nomad Collective",
            "source": "WhatsApp",
            "text": "eh one more thing — our client Marcus gets quite particular about music choices. No mainstream pop please. He prefers indie acoustic or ambient sounds. Also always credit the photographer in the caption, he's very particular about this."
        },
        {
            "client": "TechVentures SG",
            "source": "Brief",
            "text": "TechVentures SG requires all content to be data-driven and professional. Always cite statistics when possible. Their brand voice is authoritative and confident. They prefer dark backgrounds with white text for all designed assets. All content must be approved by their marketing director James Wong before publishing. Singapore English is preferred — not American English."
        },
        {
            "client": "Casa Living",
            "source": "Meeting Notes",
            "text": "Casa Living is a Singapore lifestyle brand targeting HDB homeowners. They want content that feels aspirational but achievable — not luxury, not budget. Warm tones, natural light photography only. They love before-and-after content. Their audience responds well to Singlish captions mixed with standard English. Post timing: 7-9am and 7-9pm SGT only for best engagement."
        }
    ]

    for s in samples:
        extracted = extract_preferences(s["text"], s["client"], s["source"])
        store_in_chromadb(s["client"], s["source"], s["text"], extracted)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px">
        <div style="font-size:0.95rem;font-weight:600;">Client Memory</div>
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.45);margin-top:2px;">
            Hubble Collective
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    total = collection.count()
    clients = get_all_clients()

    st.markdown(f"""
    <div style="padding:4px 0 16px">
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.4);
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">
            Database
        </div>
        <div style="font-size:1.4rem;font-weight:500;color:white">{total}</div>
        <div style="font-size:0.72rem;color:rgba(255,255,255,0.45)">
            knowledge entries
        </div>
        <div style="font-size:1.4rem;font-weight:500;color:white;margin-top:10px">
            {len(clients)}
        </div>
        <div style="font-size:0.72rem;color:rgba(255,255,255,0.45)">clients stored</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if clients:
        st.markdown("""
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.4);
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">
            Clients
        </div>
        """, unsafe_allow_html=True)
        for c in clients:
            st.markdown(f"""
            <div style="font-size:0.82rem;color:rgba(255,255,255,0.7);
                        padding:4px 0;border-bottom:0.5px solid rgba(255,255,255,0.08)">
                {c}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    if st.button("Load sample clients"):
        if total == 0:
            with st.spinner("Loading sample data..."):
                seed_sample_data()
            st.success("Sample clients loaded!")
            st.rerun()
        else:
            st.warning("Data already exists.")

    if st.button("Clear all data"):
        chroma.delete_collection("client_memory")
        chroma = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma.get_or_create_collection("client_memory")
        st.success("Cleared!")
        st.rerun()


# ── Main tabs ────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Ask About a Client", "Add Client Knowledge"])


# ══════════════════════════════════════════════════════════════
# TAB 1: QUERY
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:600;color:#0f172a;margin-bottom:4px;">
        Ask anything about a client
    </div>
    <div style="font-size:0.82rem;color:#64748b;margin-bottom:20px;">
        The system searches all stored knowledge and answers instantly
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        question = st.text_input(
            "Question",
            placeholder='e.g. "What does Bloom Studio prefer for captions?"',
            label_visibility="collapsed"
        )
    with col2:
        client_filter = st.selectbox(
            "Filter by client",
            ["All clients"] + get_all_clients(),
            label_visibility="collapsed"
        )

    ask_btn = st.button("Ask →", key="ask_btn")

    if ask_btn:
        if not question.strip():
            st.error("Please enter a question.")
        elif collection.count() == 0:
            st.warning("No client data yet. Load sample clients or add knowledge first.")
        else:
            with st.spinner("Searching client memory..."):
                result = query_client_memory(question, client_filter)

            st.markdown("""
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;
                        text-transform:uppercase;color:#94a3b8;margin-bottom:8px;">
                Answer
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="answer-box">{result['answer']}</div>
            """, unsafe_allow_html=True)

            if result["sources"]:
                st.markdown("""
                <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;
                            text-transform:uppercase;color:#94a3b8;
                            margin:14px 0 8px;">
                    Sources
                </div>
                """, unsafe_allow_html=True)
                for s in result["sources"]:
                    st.markdown(f'<span class="source-tag">{s}</span>',
                                unsafe_allow_html=True)

    # Sample questions
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;
                text-transform:uppercase;color:#94a3b8;margin:24px 0 10px;">
        Try these questions
    </div>
    """, unsafe_allow_html=True)

    sample_questions = [
        "What language does Bloom Studio prefer?",
        "How should we caption Nomad Collective's posts?",
        "What does TechVentures SG require for approval?",
        "What are Casa Living's best posting times?",
        "Which clients prefer candid photography?",
        "What music does Nomad Collective prefer?"
    ]

    cols = st.columns(3)
    for i, q in enumerate(sample_questions):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;
                        padding:10px 12px;font-size:0.78rem;color:#475569;
                        margin-bottom:8px;cursor:default;line-height:1.4">
                {q}
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2: ADD KNOWLEDGE
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:600;color:#0f172a;margin-bottom:4px;">
        Add client knowledge
    </div>
    <div style="font-size:0.82rem;color:#64748b;margin-bottom:20px;">
        Paste any raw text — WhatsApp message, email, meeting notes.
        Claude extracts and stores the key information automatically.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        new_client = st.text_input(
            "Client name",
            placeholder="e.g. Bloom Studio"
        )
    with col2:
        source_type = st.selectbox(
            "Source type",
            ["WhatsApp", "Email", "Meeting Notes",
             "Brief", "Feedback", "Other"]
        )

    raw_input = st.text_area(
        "Raw text",
        height=180,
        placeholder="Paste any message, email, or notes about this client here..."
    )

    add_btn = st.button("Extract & Store →", key="add_btn")

    if add_btn:
        if not new_client.strip():
            st.error("Please enter a client name.")
        elif not raw_input.strip():
            st.error("Please paste some text to process.")
        else:
            with st.spinner("Claude is extracting preferences..."):
                try:
                    extracted = extract_preferences(
                        raw_input, new_client, source_type
                    )
                    store_in_chromadb(
                        new_client, source_type, raw_input, extracted
                    )

                    st.success(f"Stored! {new_client}'s knowledge updated.")

                    # Show what was extracted
                    st.markdown("""
                    <div style="font-size:0.68rem;font-weight:600;
                                letter-spacing:0.1em;text-transform:uppercase;
                                color:#94a3b8;margin:16px 0 10px;">
                        Extracted
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-label">Preferences</div>',
                                    unsafe_allow_html=True)
                        for p in extracted.get("preferences", []):
                            st.markdown(
                                f'<div style="font-size:0.82rem;color:#475569;'
                                f'padding:3px 0;border-bottom:0.5px solid #f1f5f9;">'
                                f'• {p}</div>',
                                unsafe_allow_html=True
                            )
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-label">Brand Guidelines</div>',
                                    unsafe_allow_html=True)
                        for g in extracted.get("brand_guidelines", []):
                            st.markdown(
                                f'<div style="font-size:0.82rem;color:#475569;'
                                f'padding:3px 0;border-bottom:0.5px solid #f1f5f9;">'
                                f'• {g}</div>',
                                unsafe_allow_html=True
                            )
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-label">Common Revisions</div>',
                                    unsafe_allow_html=True)
                        for r in extracted.get("common_revisions", []):
                            st.markdown(
                                f'<div style="font-size:0.82rem;color:#475569;'
                                f'padding:3px 0;border-bottom:0.5px solid #f1f5f9;">'
                                f'• {r}</div>',
                                unsafe_allow_html=True
                            )
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-label">Summary</div>',
                                    unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="font-size:0.82rem;color:#475569;'
                            f'line-height:1.6;">'
                            f'{extracted.get("summary", "")}</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")