"""
Metadata generation using OpenAI API.
"""

import os
from openai import AsyncOpenAI
from models import ComponentMetadata


async def generate_metadata(
    component_name: str,
    html_snippet: str,
    code_blocks: list[str]
) -> ComponentMetadata | None:
    """
    Generate component metadata using OpenAI.
    
    Args:
        component_name: Name of the component
        html_snippet: HTML content snippet
        code_blocks: List of code blocks from the page
        
    Returns:
        ComponentMetadata object or None if generation fails
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  ⊘ OPENAI_API_KEY not set, skipping metadata generation")
            return None
        
        client = AsyncOpenAI(api_key=api_key)
        
        # Prepare context
        code_text = "\n---\n".join(code_blocks[:3])  # Limit to first 3 blocks
        
        prompt = f"""Analyze this component and generate metadata.

Component: {component_name}

Code samples:
{code_text}

Return JSON with exactly this structure:
{{
  "component_type": "primitive|composite|layout|form|navigation|feedback|overlay|other",
  "style": ["unstyled", "customizable", "styled", or similar - array of 1-3 tags],
  "complexity": 0 (simple/atomic), 1 (medium/composed), or 2 (complex/stateful),
  "description": "Brief 1-2 sentence description"
}}

Be concise and accurate. Return only valid JSON."""

        response = await client.chat.completions.create(
            model="gpt-4-mini",
            messages=[
                {"role": "system", "content": "You are an expert frontend component analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        import json
        data = json.loads(content)
        
        metadata = ComponentMetadata(**data)
        print(f"  ✓ Metadata: {metadata.component_type} (complexity: {metadata.complexity})")
        
        return metadata
        
    except Exception as e:
        print(f"  ✗ Metadata generation failed: {e}")
        return None