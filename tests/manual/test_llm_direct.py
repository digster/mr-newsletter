"""Direct test for LLM service - bypasses UI to debug API issues."""

import asyncio
import logging
import os

# Force LLM enabled for testing (bypasses env/settings check)
os.environ["LLM_ENABLED"] = "true"
os.environ["LLM_API_BASE_URL"] = os.environ.get("LLM_API_BASE_URL", "http://localhost:1234/v1")

# Enable verbose logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s")

# Clear settings cache so it picks up our env vars
from src.config.settings import get_settings
get_settings.cache_clear()

from src.services.llm_service import LLMService


async def test_llm():
    """Test LLM service in isolation."""
    print("=" * 60)
    print("LLM Service Direct Test")
    print("=" * 60)

    service = LLMService()  # No user_settings - uses env vars only

    # Step 1: Check if enabled
    print("\n[1] Checking if LLM is enabled...")
    enabled = service.is_enabled()
    print(f"    LLM Enabled: {enabled}")

    if not enabled:
        print("\n    LLM is disabled! This should not happen since we set LLM_ENABLED=true")
        return

    # Step 2: Test connection
    print("\n[2] Testing connection to LLM server...")
    connected, msg = await service.check_connection()
    print(f"    Connected: {connected}")
    print(f"    Message: {msg}")

    if not connected:
        print("\n    Connection failed! Make sure LM Studio is running.")
        print("    LM Studio should be running at http://localhost:1234")
        return

    # Step 3: Test summarization with mock text
    print("\n[3] Testing summarization with mock email...")
    result = await service.summarize_email(
        subject="Weekly Python Newsletter #42",
        body_text="""
        Hello fellow Pythonistas!

        This week we have some exciting updates:

        1. Python 3.13 Beta Released
           The new beta includes improved error messages and faster startup times.

        2. New PEP: Pattern Matching Enhancements
           PEP 7XX proposes new pattern matching features for dictionaries.

        3. Django 5.0 Coming Soon
           Major async improvements and better type hints support.

        Happy coding!
        """,
        sender_name="Python Weekly",
    )

    print(f"\n    Success: {result.success}")
    print(f"    Model: {result.model}")
    print(f"    Error: {result.error}")
    print(f"\n    Summary:")
    print(f"    {'-' * 50}")
    if result.summary:
        print(f"    {result.summary}")
    else:
        print("    (No summary returned)")
    print(f"    {'-' * 50}")

    # Final verdict
    print("\n" + "=" * 60)
    if result.success and result.summary:
        print("SUCCESS: LLM API is working correctly!")
        print("   The problem is likely in the UI/database layer.")
    else:
        print("FAILED: LLM API returned no summary.")
        print(f"   Error: {result.error}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_llm())
