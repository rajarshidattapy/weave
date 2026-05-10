"""
Retrieval Agent — converts natural language prompts into component retrieval.

Pipeline: prompt → tag expansion → DB search → compatibility ranking → results
"""
import logging
import json
import os

from openai import OpenAI
from database.models import search_components_by_tags, get_all_components, get_compatible_components

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def retrieve_components(prompt: str, limit: int = 10) -> dict:
    """
    Retrieve components matching a natural language prompt.

    Returns dict with:
      - components: list of matching component dicts
      - expanded_tags: the tags extracted from the prompt
    """
    logger.info(f"Retrieving components for: {prompt}")

    # Step 1: Expand prompt into searchable tags
    expanded_tags = _expand_prompt(prompt)
    logger.info(f"Expanded tags: {expanded_tags}")

    # Step 2: Search DB by tags
    results = search_components_by_tags(expanded_tags, limit=limit * 2)

    if not results:
        # Fallback: return all components if no tag match
        logger.info("No tag matches — returning all components")
        results = get_all_components(limit=limit)

    # Step 3: Re-rank results by relevance to original prompt
    if len(results) > limit:
        results = _rerank(prompt, results, limit)

    return {
        "components": results[:limit],
        "expanded_tags": expanded_tags,
    }


def _expand_prompt(prompt: str) -> list[str]:
    """Use LLM to expand a prompt into searchable tags."""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a frontend component search query expander. "
                        "Given a user prompt, extract relevant search tags.\n\n"
                        "Return a JSON object with a single key 'tags' containing an array of strings.\n"
                        "Include:\n"
                        "- Semantic tags: hero, pricing, footer, cta, navbar, card, etc.\n"
                        "- Visual tags: glassmorphism, dark, animated, gradient, minimal, etc.\n"
                        "- Technical tags: framer-motion, tailwind, shadcn, etc.\n"
                        "- Usage tags: ai-startup, landing-page, saas, portfolio, etc.\n\n"
                        "Return 5-15 tags total. Be generous with related terms."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        tags = parsed.get("tags", [])
        return [t.lower() for t in tags if isinstance(t, str)]

    except Exception as e:
        logger.error(f"Prompt expansion failed: {e}")
        # Fallback: split prompt into words
        return [w.lower() for w in prompt.split() if len(w) > 2]


def _rerank(prompt: str, components: list[dict], limit: int) -> list[dict]:
    """Re-rank components by relevance to the original prompt using LLM."""
    try:
        # Build a summary of each component for ranking
        summaries = []
        for i, c in enumerate(components[:30]):  # Cap at 30 for token limits
            summaries.append(f"{i}: {c.get('name', 'unknown')} — {c.get('description', 'N/A')}")

        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a component relevance ranker. Given a user prompt and a list of "
                        "components, return the indices of the most relevant components in order of "
                        "relevance. Return a JSON object with key 'indices' containing an array of "
                        "integer indices."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Prompt: {prompt}\n\n"
                        f"Components:\n" + "\n".join(summaries) + "\n\n"
                        f"Return the top {limit} most relevant indices."
                    ),
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        indices = parsed.get("indices", list(range(limit)))

        ranked = []
        for idx in indices:
            if isinstance(idx, int) and 0 <= idx < len(components):
                ranked.append(components[idx])
        return ranked if ranked else components[:limit]

    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        return components[:limit]
