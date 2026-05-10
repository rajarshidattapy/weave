"""
Retrieval Agent — converts natural language prompts into component retrieval.

Pipeline:
  prompt → tag expansion → tag search → text search fallback → rerank → results
"""
import logging
import json
import os

from openai import OpenAI
from database.models import (
    search_components_by_tags,
    search_components_by_text,
    get_all_components,
    get_compatible_components,
)

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def retrieve_components(prompt: str, limit: int = 10, context: str = None) -> dict:
    """
    Retrieve components matching a natural language prompt.

    Returns dict with:
      - components: list of matching component dicts
      - expanded_tags: tags extracted from the prompt
    """
    logger.info(f"Retrieving components for: {prompt}")
    if context:
        logger.info(f"Sandbox context: {context}")

    # Step 1: Expand prompt into searchable tags
    expanded_tags = _expand_prompt(prompt, context)
    logger.info(f"Expanded tags: {expanded_tags}")

    # Step 2: Tag-based search (primary)
    results = search_components_by_tags(expanded_tags, limit=limit * 3)

    # Step 3: Text search fallback — catches components with sparse/no tags
    if not results:
        logger.info("No tag matches — trying text search")
        # Try each key term from the prompt individually
        key_terms = [t for t in expanded_tags if len(t) > 3][:5]
        for term in key_terms:
            text_results = search_components_by_text(term, limit=limit * 2)
            if text_results:
                results = text_results
                logger.info(f"Text search matched {len(results)} components for term '{term}'")
                break

    # Step 4: Last resort — return everything and let rerank decide
    if not results:
        logger.info("No text matches — returning all components for reranking")
        results = get_all_components(limit=limit * 3)

    if not results:
        logger.warning("Database is empty — run index_all.py to scrape libraries first")
        return {"components": [], "expanded_tags": expanded_tags}

    # Step 5: Rerank by relevance when we have more than needed
    if len(results) > limit:
        results = _rerank(prompt, results, limit, context)

    return {
        "components": results[:limit],
        "expanded_tags": expanded_tags,
    }


def _expand_prompt(prompt: str, context: str = None) -> list[str]:
    """Use LLM to expand a prompt into searchable tags."""
    try:
        user_content = prompt
        if context:
            user_content = (
                f"{prompt}\n\n"
                f"Sandbox context: {context}\n"
                "Prefer tags for components that complement what's already in use. "
                "Avoid suggesting duplicates of already-present components."
            )
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
                        "- Component type tags: button, accordion, dialog, card, navbar, hero, etc.\n"
                        "- Semantic tags: cta, pricing, footer, testimonials, dashboard, form, etc.\n"
                        "- Visual tags: glassmorphism, dark, animated, gradient, minimal, etc.\n"
                        "- Technical tags: framer-motion, tailwind, shadcn, radix, etc.\n"
                        "- Usage tags: ai-startup, landing-page, saas, portfolio, etc.\n\n"
                        "IMPORTANT: Always include the literal component type word (e.g. if the user "
                        "says 'button', include 'button' as a tag). Return 5-15 tags."
                    ),
                },
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        tags = parsed.get("tags", [])
        expanded = [t.lower() for t in tags if isinstance(t, str)]

        # Always include significant words from the original prompt
        for word in prompt.lower().split():
            word = word.strip(".,!?\"'")
            if len(word) > 2 and word not in expanded:
                expanded.append(word)

        return expanded

    except Exception as e:
        logger.error(f"Prompt expansion failed: {e}")
        return [w.lower().strip(".,!?") for w in prompt.split() if len(w) > 2]


def _rerank(prompt: str, components: list[dict], limit: int, context: str = None) -> list[dict]:
    """Re-rank components by relevance to the original prompt using LLM."""
    try:
        summaries = []
        for i, c in enumerate(components[:30]):
            summaries.append(
                f"{i}: {c.get('name', 'unknown')} "
                f"[{c.get('source_library', '')}] — {c.get('description', 'N/A')[:80]}"
            )

        user_content = f"Prompt: {prompt}\n"
        if context:
            user_content += (
                f"Context: {context}\n"
                "Prefer components that complement what's already in the sandbox. "
                "De-prioritize components that duplicate ones already present.\n"
            )
        user_content += (
            f"\nComponents:\n" + "\n".join(summaries) +
            f"\n\nReturn the top {limit} most relevant indices."
        )

        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a component relevance ranker. Given a user prompt and a list of "
                        "components, return the indices of the most relevant components in order of "
                        "relevance. Return a JSON object with key 'indices' (array of integers)."
                    ),
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        indices = json.loads(response.choices[0].message.content).get(
            "indices", list(range(limit))
        )
        ranked = [
            components[i]
            for i in indices
            if isinstance(i, int) and 0 <= i < len(components)
        ]
        return ranked if ranked else components[:limit]

    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        return components[:limit]
