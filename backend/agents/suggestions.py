"""
Suggestions Agent — analyzes sandbox state and generates actionable UI improvement suggestions.

Input:  sandbox context string (e.g. "Sandbox already uses: Button, Card (shadcn/ui)")
Output: list of suggestions, each with a title, description, search_query, and top matched component
"""
import json
import logging
import os

from openai import OpenAI
from database.models import search_components_by_tags, search_components_by_text

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def suggest_improvements(context: str, limit: int = 5) -> dict:
    """
    Given a sandbox context string, use the LLM to generate improvement suggestions.
    Each suggestion is enriched with the top matching component from the DB.
    """
    if not context or not context.strip():
        context = "Empty sandbox — no components added yet."

    logger.info(f"Generating suggestions for context: {context[:120]}")

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior UI/UX advisor for modern React web apps. "
                        "Given a description of components currently in a sandbox, "
                        "suggest concrete, actionable improvements the developer can make next.\n\n"
                        "Return a JSON object with key 'suggestions', an array of objects with:\n"
                        "- title: short imperative phrase (max 6 words, e.g. 'Add a testimonials section')\n"
                        "- description: one sentence explaining why this improves the UI\n"
                        "- search_query: natural language query to find the ideal component "
                        "(e.g. 'testimonials social proof cards with avatars')\n\n"
                        "Rules:\n"
                        "- Focus on what is MISSING or WEAK, not what is already present\n"
                        "- Be specific — 'Add animated hero CTA' beats 'Improve buttons'\n"
                        "- Cover variety: layout, conversion, feedback, navigation, visual polish\n"
                        f"- Return exactly {limit} suggestions ordered by impact"
                    ),
                },
                {
                    "role": "user",
                    "content": f"Current sandbox state:\n{context}",
                },
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        parsed = json.loads(response.choices[0].message.content)
        raw = parsed.get("suggestions", [])

    except Exception as e:
        logger.error(f"LLM suggestion generation failed: {e}")
        raw = []

    enriched = []
    for s in raw[:limit]:
        query = s.get("search_query") or s.get("title") or ""
        top = _find_top_component(query)
        enriched.append({
            "title": s.get("title", ""),
            "description": s.get("description", ""),
            "search_query": query,
            "top_component": top,
        })

    return {"suggestions": enriched}


def _find_top_component(query: str) -> dict | None:
    """Find the single best matching component for a search query."""
    words = [w for w in query.lower().split() if len(w) > 3]
    if not words:
        return None

    # Tag search first
    results = search_components_by_tags(words[:6], limit=3)
    if results:
        return results[0]

    # Text search fallback
    for word in words[:4]:
        results = search_components_by_text(word, limit=3)
        if results:
            return results[0]

    return None
