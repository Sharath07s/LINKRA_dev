import re
from typing import Dict, Any, Optional
from app.schemas.copilot import CopilotIntent
from app.ai.provider import FallbackManager

class IntentRouter:
    """Lightweight rule-based intent router with LLM fallback."""
    
    KEYWORD_MAP = {
        CopilotIntent.EVIDENCE_LOOKUP: ["evidence", "proof", "source", "document", "where is this from", "support", "supporting evidence"],
        CopilotIntent.ANOMALY_EXPLANATION: ["anomaly", "anomalous", "flagged", "weird", "unusual", "suspicious structure"],
        CopilotIntent.POTENTIAL_LINK_EXPLANATION: ["potential link", "suggested link", "why is this linked", "why link", "suggested connection", "potential connection", "predict"],
        CopilotIntent.RELATIONSHIP_LOOKUP: ["relationship", "connection", "connect", "link", "how are they related", "associates", "knows"],
        CopilotIntent.INVESTIGATION_SUMMARY: ["summarize", "summary", "brief", "what is this investigation about"],
        CopilotIntent.COMPARISON: ["compare", "difference between", "versus", "vs"],
        CopilotIntent.GRAPH_EXPLORATION: ["graph", "network", "around", "hops", "neighbors", "surrounding"],
        CopilotIntent.ENTITY_LOOKUP: ["who is", "what is", "details about", "tell me about"],
        CopilotIntent.COMMUNITY_LOOKUP: ["community", "communities", "louvain", "leiden", "grouping"],
    }

    @classmethod
    def get_intent(cls, message: str) -> CopilotIntent:
        """Determines intent from the user message."""
        msg_lower = message.lower()
        
        # 1. Rule-based fast matching
        for intent, keywords in cls.KEYWORD_MAP.items():
            if any(re.search(rf"\b{kw}\b", msg_lower) for kw in keywords):
                return intent
        
        # 2. LLM fallback if keywords fail
        prompt = f"""You are an intent classifier for a criminal intelligence copilot.
Categorize the following user message into exactly one of these intents:
{', '.join([i.name for i in CopilotIntent])}

Message: "{message}"

Return ONLY the intent string and nothing else."""
        
        try:
            response = FallbackManager.execute_with_fallback(prompt=prompt, temperature=0.0)
            intent_str = response["result"].strip().upper()
            try:
                return CopilotIntent(intent_str)
            except ValueError:
                pass
        except Exception:
            pass # Fallback to general intelligence query

        return CopilotIntent.GENERAL_INTELLIGENCE_QUERY
