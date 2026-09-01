import uuid
import datetime
import json
import logging
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.chat import ChatQuery, ChatResponse
from app.ai.provider import FallbackManager
from app.ai.intents.engine import IntentEngine
from app.ai.query_planner.planner import QueryPlanner
from app.ai.rag.vector_search import VectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Keyword-based intent fallback (no LLM needed) ──────────────
KEYWORD_MAP = {
    "hotspots": ["hotspot", "hot spot", "high crime", "danger zone", "unsafe"],
    "trends": ["trend", "increase", "decrease", "compare", "statistics", "stats", "analysis"],
    "suspect_search": ["suspect", "offender", "criminal", "accused", "wanted", "gang"],
    "vehicle_search": ["vehicle", "car", "bike", "registration", "stolen vehicle"],
    "station_search": ["station", "police station", "thana"],
    "crime_search": ["theft", "robbery", "murder", "fraud", "case", "fir", "crime", "assault", "burglary", "cybercrime", "kidnapping"],
    "suspect_network": ["associates", "network of suspect", "friends", "connected to suspect"],
    "vehicle_network": ["linked to vehicle", "common vehicles", "shared vehicles"],
    "crime_network": ["network around fir", "network around crime"],
    "repeat_offenders": ["repeat offenders", "repeat offender", "top criminals"],
    "criminal_cluster": ["high risk networks", "criminal cluster", "criminal clusters"],
}

def _keyword_intent(query: str) -> dict:
    """Deterministic intent extraction using keyword matching — zero LLM cost."""
    q = query.lower()
    for intent, keywords in KEYWORD_MAP.items():
        if any(kw in q for kw in keywords):
            # Simple entity extraction
            crime_type = None
            for ct in ["theft", "robbery", "murder", "fraud", "assault", "burglary", "cybercrime", "kidnapping"]:
                if ct in q:
                    crime_type = ct
                    break
            district = None
            for d in ["mysuru", "bengaluru", "mangaluru", "hubballi", "belagavi", "shivamogga", "tumakuru", "davangere", "kalaburagi", "ballari", "delhi", "mumbai", "chennai", "kolkata"]:
                if d in q:
                    district = d.capitalize()
                    break
            return {"intent": intent, "crime_type": crime_type, "district": district, "time_frame": None}
    return {"intent": "general", "crime_type": None, "district": None, "time_frame": None}


@router.post("/", response_model=ChatResponse)
def chat_with_ai(
    *,
    db: Session = Depends(deps.get_db),
    query_in: ChatQuery,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    KCIA AI Pipeline:
      1. Intent Extraction (LLM with keyword fallback)
      2. Database Query Execution
      3. LLM Summarization (with raw-data fallback)
    """

    # ── Step 1: Intent Extraction ────────────────────────────────
    intent_result = IntentEngine.extract_intent(query_in.query)
    intent_data = intent_result.get("intent_data", {})

    if intent_result.get("status") == "error":
        # All providers down → use keyword matching
        intent_data = _keyword_intent(query_in.query)
        logger.info(f"Using keyword-based intent: {intent_data}")

    intent_label = intent_data.get("intent", "general")

    # ── Step 2: Database Query ───────────────────────────────────
    db_context = QueryPlanner.execute_intent(db, intent_data)
    records = db_context.get("data", [])
    record_count = db_context.get("record_count", 0)

    # ── Step 2.5: RAG Context Retrieval ──────────────────────────
    rag_context = ""
    retrieved_chunks = []
    if intent_label == "crime_search" or intent_label == "suspect_search":
        try:
            vector_store = VectorStore()
            retrieved_chunks = vector_store.semantic_search(query_in.query, top_k=3)
            if retrieved_chunks:
                rag_context = "\n\nRelevant Document Context:\n"
                for i, chunk in enumerate(retrieved_chunks):
                    rag_context += f"--- Source: {chunk['doc_id']} (Confidence: {chunk['similarity']}) ---\n"
                    rag_context += f"{chunk['content']}\n"
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

    # ── Step 3: LLM Summarization ────────────────────────────────
    summarization_prompt = f"""You are LINKRA — AI-Powered Criminal Intelligence Network.
The user asked: "{query_in.query}"

Extracted intent: {intent_label}
Database returned {record_count} records:
{json.dumps(records, indent=2, default=str)}
{rag_context}

Instructions:
- Summarize these results in a natural, professional, concise paragraph.
- If data is empty, say so honestly.
- Include key numbers and names.
- Format as markdown with bullet points where appropriate."""

    try:
        summary_response = FallbackManager.execute_with_fallback(
            prompt=summarization_prompt,
            temperature=0.3,
        )
        final_message = summary_response["result"]
        provider_used = summary_response["provider"]
    except Exception:
        # Graceful degradation — show formatted raw data
        if record_count > 0 or retrieved_chunks:
            final_message = _format_raw_data(intent_label, records, retrieved_chunks)
        else:
            final_message = f"No records found for your query. Try broadening your search."
        provider_used = "system_fallback"

    return ChatResponse(
        message=final_message,
        provider=provider_used,
        timestamp=datetime.datetime.utcnow().isoformat(),
        status="success",
        intent=intent_label,
        structured_data=records if records else None,
        record_count=record_count,
    )


def _format_raw_data(intent: str, records: list, retrieved_chunks: list = None) -> str:
    """Human-readable markdown when AI providers are offline."""
    INTENT_TITLES = {
        "crime_search": "🔍 Crime Records Found",
        "suspect_search": "🕵️ Suspect Intelligence",
        "vehicle_search": "🚗 Vehicle Records",
        "station_search": "🏛️ Police Station Information",
        "trends": "📊 Crime Trend Analysis",
        "hotspots": "🗺️ Crime Hotspot Analysis",
        "suspect_network": "🕸️ Suspect Network",
        "vehicle_network": "🕸️ Vehicle Network",
        "crime_network": "🕸️ Crime Network",
        "repeat_offenders": "⚠️ Repeat Offenders",
        "criminal_cluster": "⚠️ High-Risk Networks",
        "general": "📋 System Overview",
    }
    title = INTENT_TITLES.get(intent, "📋 Query Results")
    lines = [f"**{title}** — {len(records)} record(s)\n"]

    if intent == "crime_search":
        lines.append("| FIR | Title | Status | District | Date |")
        lines.append("|-----|-------|--------|----------|------|")
        for r in records:
            lines.append(f"| `{r.get('fir_number','')}` | {r.get('title','')} | {r.get('status','')} | {r.get('district','')} | {r.get('date','')[:10]} |")
    elif intent == "suspect_search":
        lines.append("| Name | Alias | Risk Score | Linked Cases |")
        lines.append("|------|-------|------------|--------------|")
        for r in records:
            lines.append(f"| {r.get('name','')} | {r.get('alias','—')} | {r.get('risk_score',0):.1f} | {r.get('linked_cases',0)} |")
    elif intent == "trends":
        lines.append("| Crime Type | Count |")
        lines.append("|------------|-------|")
        for r in records:
            lines.append(f"| {r.get('crime_type','')} | {r.get('count',0)} |")
    elif intent == "hotspots":
        lines.append("| District | Incidents |")
        lines.append("|----------|-----------|")
        for r in records:
            lines.append(f"| {r.get('district','')} | {r.get('count',0)} |")
    elif intent == "station_search":
        lines.append("| Station | Code | District |")
        lines.append("|---------|------|----------|")
        for r in records:
            lines.append(f"| {r.get('station_name','')} | `{r.get('station_code','')}` | {r.get('district','')} |")
    elif intent == "vehicle_search":
        lines.append("| Registration | Type | Owner |")
        lines.append("|-------------|------|-------|")
        for r in records:
            lines.append(f"| `{r.get('registration','')}` | {r.get('type','—')} | {r.get('owner','—')} |")
    else:
        for r in records:
            lines.append(f"- **{r.get('metric','')}**: {r.get('value','')}")

    if retrieved_chunks:
        lines.append("\n### 📄 Related Document Context (RAG)")
        for chunk in retrieved_chunks:
            lines.append(f"> **Source:** {chunk['doc_id']} (Confidence: {chunk['similarity']})")
            lines.append(f"> {chunk['content'][:300]}...\n")

    lines.append("\n*AI providers are currently offline. Showing direct database intelligence.*")
    return "\n".join(lines)
