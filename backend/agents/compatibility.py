"""
Compatibility Agent — generates component compatibility scores.
"""
import logging
import json
import os
from openai import OpenAI
from database.models import get_all_components, insert_compatibility

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def compute_compatibility(component: dict) -> list[dict]:
    """Compute compatibility scores between a component and all others in DB."""
    all_components = get_all_components(limit=200)
    others = [c for c in all_components if c["id"] != component["id"]]
    if not others:
        return []

    summaries = []
    for c in others[:30]:
        summaries.append(f"- {c['id']}: {c.get('name','')} ({', '.join(c.get('tags',[])[:5])})")

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": (
                    "You are a UI component compatibility analyzer. Given a source component "
                    "and a list of other components, score how well each pairs with the source "
                    "(0.0 = incompatible, 1.0 = perfect match). Consider style, animation, "
                    "spacing, theme, and semantic pairing.\n"
                    "Return JSON: {\"scores\": [{\"id\": \"...\", \"score\": 0.8}, ...]}"
                )},
                {"role": "user", "content": (
                    f"Source: {component.get('name','')} — tags: {component.get('tags',[])} "
                    f"styles: {component.get('styles',[])}\n\nOthers:\n" + "\n".join(summaries)
                )},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.choices[0].message.content)
        scores = parsed.get("scores", [])
        for s in scores:
            if s.get("score", 0) >= 0.4:
                insert_compatibility(component["id"], s["id"], s["score"])
        return scores
    except Exception as e:
        logger.error(f"Compatibility analysis failed: {e}")
        return []
