import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API key
if not os.getenv("OPENAI_API_KEY"):
    print("\n⚠️  WARNING: OPENAI_API_KEY not set in .env")
    print("   Metadata generation will be skipped")
    print("   Add your key to .env to enable full functionality\n")

from graph import app
from sources import SOURCES
from storage import load_components


async def main():
    """Main entrypoint for the indexer."""
    
    print("\n" + "="*60)
    print("COMPONENT INDEXER - shadcn/ui")
    print("="*60)
    print()
    
    # Use shadcn source
    source_config = SOURCES["shadcn"]
    
    # Initialize state
    initial_state = {
        "source": "shadcn",
        "index_url": source_config["index_url"],
        "base_url": source_config["base_url"],
        "index_html": "",
        "component_urls": [],
        "current_url": "",
        "current_name": "",
        "current_html": "",
        "code_blocks": [],
        "screenshot_path": None,
        "metadata": None,
        "processed_count": 0,
        "total_count": 0
    }
    
    # Run the indexing pipeline
    try:
        result = await app.ainvoke(initial_state)
        
        # Display final summary
        components = load_components()
        
        print("\n" + "="*60)
        print("INDEXING COMPLETE")
        print("="*60)
        print(f"\n✓ Total components indexed: {len(components)}")
        print(f"✓ Database: data/components.json")
        print(f"✓ Screenshots: data/screenshots/")
        print()
        
        # Show statistics
        if components:
            complexity_dist = {}
            for c in components:
                if c.metadata:
                    ct = c.metadata.complexity
                    complexity_dist[ct] = complexity_dist.get(ct, 0) + 1
            
            if complexity_dist:
                print("Complexity distribution:")
                labels = {0: "Simple", 1: "Medium", 2: "Complex"}
                for level in sorted(complexity_dist.keys()):
                    print(f"  {labels[level]}: {complexity_dist[level]}")
            print()
        
    except Exception as e:
        print(f"\n✗ Error during indexing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())