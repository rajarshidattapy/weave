"""
Metadata Agent — generates semantic, visual, usage, and technical tags.

Input:  component name + code + description
Output: tags dict with semantic, visual, usage, technical arrays
"""
import logging
import json
import os

from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Load system prompt
_PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


def _load_prompt() -> str:
    """Load the metadata system prompt."""
    path = os.path.join(_PROMPT_DIR, "metadata_prompt.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    # Inline fallback
    return (
        "You are a frontend component classifier. Given a component's name, code, "
        "and description, generate classification tags.\n\n"
        "Return a JSON object with:\n"
        '- "semantic": array of semantic tags (hero, pricing, footer, cta, navbar, dashboard, card, form, etc.)\n'
        '- "visual": array of visual style tags (glassmorphism, bento, minimal, animated, dark, gradient, retro, modern, etc.)\n'
        '- "usage": array of usage context tags (ai-startup, portfolio, landing-page, saas, dashboard, e-commerce, etc.)\n'
        '- "technical": array of technical dependency tags (framer-motion, threejs, tailwind, shadcn, radix, etc.)\n\n'
        "Return 2-6 tags per category. Be specific and accurate."
    )


def generate_metadata(name: str, tsx_code: str = "", description: str = "") -> dict:
    """
    Generate classification tags for a component.

    Returns dict with keys: tags (combined list), styles, semantic, visual, usage, technical
    """
    logger.info(f"Generating metadata for: {name}")

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _load_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"Component: {name}\n\n"
                        f"Description: {description or 'N/A'}\n\n"
                        f"Code:\n```tsx\n{tsx_code[:3000]}\n```"
                    ),
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        semantic = parsed.get("semantic", [])
        visual = parsed.get("visual", [])
        usage = parsed.get("usage", [])
        technical = parsed.get("technical", [])

        return {
            "tags": semantic + usage + technical,
            "styles": visual,
            "semantic": semantic,
            "visual": visual,
            "usage": usage,
            "technical": technical,
            # Embedding text for future vector search
            "embedding_text": f"{name}. {description}. Tags: {', '.join(semantic + visual + usage + technical)}",
        }

    except Exception as e:
        logger.error(f"Metadata generation failed for {name}: {e}")
        return {
            "tags": [],
            "styles": [],
            "semantic": [],
            "visual": [],
            "usage": [],
            "technical": [],
            "embedding_text": f"{name}. {description}",
        }
