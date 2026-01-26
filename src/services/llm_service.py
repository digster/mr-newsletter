"""LLM service for AI-powered email summarization."""

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from openai import OpenAI

from src.config.settings import get_settings
from src.models.user_settings import UserSettings
from src.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)

# System prompt for email summarization
SUMMARIZATION_PROMPT = """You are a helpful assistant that summarizes newsletter emails.
Create a concise summary of the email in 2-4 sentences.
Focus on the main points, key takeaways, and any action items.
Be direct and informative. Do not include phrases like "This email..." or "The newsletter...".
Just state the content directly."""

# Maximum input length to avoid token limits (roughly 8000 chars ~ 2000 tokens)
MAX_INPUT_LENGTH = 8000


@dataclass
class SummarizationResult:
    """Result of an email summarization attempt."""

    success: bool
    summary: str | None = None
    model: str | None = None
    error: str | None = None


@dataclass
class LLMConfig:
    """Resolved LLM configuration from all sources."""

    enabled: bool
    api_base_url: str
    api_key: str
    model: str
    max_tokens: int
    temperature: float


class LLMService:
    """Service for LLM-powered operations using OpenAI-compatible APIs."""

    def __init__(self, user_settings: UserSettings | None = None):
        """Initialize LLM service.

        Args:
            user_settings: Optional user settings for configuration override.
        """
        self.user_settings = user_settings
        self._client: OpenAI | None = None

    def _get_config(self) -> LLMConfig:
        """Get resolved LLM configuration.

        Priority: UserSettings (database) -> Environment variables -> Defaults
        """
        settings = get_settings()
        us = self.user_settings

        # Resolve each setting with priority chain
        enabled = us.llm_enabled if us else settings.llm_enabled
        api_base_url = (
            (us.llm_api_base_url if us and us.llm_api_base_url else None)
            or settings.llm_api_base_url
        )
        model = (
            (us.llm_model if us and us.llm_model else None)
            or settings.llm_model
        )
        max_tokens = (
            us.llm_max_tokens if us else settings.llm_max_tokens
        )
        temperature = (
            us.llm_temperature if us else settings.llm_temperature
        )

        # Handle API key - decrypt from UserSettings or use env var
        api_key = ""
        if us and us.llm_api_key_encrypted:
            try:
                api_key = decrypt_value(us.llm_api_key_encrypted)
            except Exception:
                logger.warning("Failed to decrypt stored API key, falling back to env")
                api_key = settings.llm_api_key
        else:
            api_key = settings.llm_api_key

        return LLMConfig(
            enabled=enabled,
            api_base_url=api_base_url,
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            config = self._get_config()
            self._client = OpenAI(
                base_url=config.api_base_url,
                api_key=config.api_key or "not-needed",  # LM Studio doesn't require key
            )
        return self._client

    def _get_available_model(self) -> str | None:
        """Get first available model from the LLM server.

        This is useful for LM Studio which requires a specific model name
        and doesn't accept 'default' as a model identifier.

        Returns:
            Model ID string if available, None otherwise.
        """
        try:
            client = self._get_client()
            models = client.models.list()
            model_list = list(models)
            if model_list:
                model_id = model_list[0].id
                logger.debug(f"Auto-detected model: {model_id}")
                return model_id
        except Exception as e:
            logger.debug(f"Could not fetch models: {e}")
        return None

    def is_enabled(self) -> bool:
        """Check if LLM summarization is enabled."""
        return self._get_config().enabled

    async def check_connection(self) -> tuple[bool, str]:
        """Test connection to the LLM API.

        Returns:
            Tuple of (success, message).
        """
        config = self._get_config()
        if not config.enabled:
            return False, "LLM summarization is disabled"

        try:
            client = self._get_client()
            # Try to list models as a connectivity check
            models = client.models.list()
            model_count = len(list(models))
            return True, f"Connected successfully ({model_count} models available)"
        except Exception as e:
            error_msg = str(e)
            if "Connection refused" in error_msg:
                return False, "Cannot connect to LLM server. Is it running?"
            return False, f"Connection failed: {error_msg}"

    def _truncate_input(self, text: str) -> str:
        """Truncate input text to avoid token limits.

        Args:
            text: Input text to truncate.

        Returns:
            Truncated text if needed.
        """
        if len(text) <= MAX_INPUT_LENGTH:
            return text
        # Truncate with ellipsis to indicate continuation
        return text[:MAX_INPUT_LENGTH - 100] + "\n\n[Content truncated for length...]"

    def _clean_response(self, text: str) -> str:
        """Clean LLM response by removing reasoning tags.

        Some models (e.g., Qwen with thinking mode) wrap their chain-of-thought
        in <think>...</think> tags. We strip these to get only the actual response.

        Args:
            text: Raw LLM response text.

        Returns:
            Cleaned text with reasoning tags removed.
        """
        # Remove <think>...</think> blocks (including multiline content)
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        return cleaned.strip()

    async def summarize_email(
        self,
        subject: str,
        body_text: str,
        sender_name: str | None = None,
    ) -> SummarizationResult:
        """Generate a summary for an email.

        Args:
            subject: Email subject line.
            body_text: Plain text email body.
            sender_name: Optional sender name for context.

        Returns:
            SummarizationResult with summary or error.
        """
        config = self._get_config()

        if not config.enabled:
            return SummarizationResult(
                success=False,
                error="LLM summarization is disabled",
            )

        if not body_text or not body_text.strip():
            return SummarizationResult(
                success=False,
                error="No email content to summarize",
            )

        # Build the user message with email content
        email_content = f"Subject: {subject}\n"
        if sender_name:
            email_content += f"From: {sender_name}\n"
        email_content += f"\n{body_text}"

        # Truncate if needed
        email_content = self._truncate_input(email_content)

        try:
            client = self._get_client()

            # Build request parameters
            request_params = {
                "messages": [
                    {"role": "system", "content": SUMMARIZATION_PROMPT},
                    {"role": "user", "content": email_content},
                ],
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
            }

            # Determine model to use
            if config.model:
                request_params["model"] = config.model
            else:
                # Auto-detect model from LM Studio (it rejects "default")
                detected_model = self._get_available_model()
                if detected_model:
                    request_params["model"] = detected_model
                    logger.info(f"Auto-detected model: {detected_model}")
                else:
                    return SummarizationResult(
                        success=False,
                        error="No model available. Please specify a model name in Settings or load a model in LM Studio.",
                    )

            response = client.chat.completions.create(**request_params)

            # Log response for debugging
            logger.info(
                f"LLM Response: choices={len(response.choices) if response.choices else 0}"
            )

            if response.choices and response.choices[0].message:
                raw_content = response.choices[0].message.content
                model_used = response.model or config.model or "unknown"

                # Log raw content details
                if raw_content:
                    logger.info(
                        f"LLM Content (raw): length={len(raw_content)}, "
                        f"preview={raw_content[:100] if len(raw_content) > 100 else raw_content}"
                    )
                else:
                    logger.warning("LLM returned None or empty content")

                # Clean the response (remove <think> tags from reasoning models)
                summary = self._clean_response(raw_content) if raw_content else None

                if summary:
                    logger.info(
                        f"LLM Content (cleaned): length={len(summary)}, "
                        f"preview={summary[:100] if len(summary) > 100 else summary}"
                    )

                # Handle empty response from LLM
                if not summary or not summary.strip():
                    return SummarizationResult(
                        success=False,
                        error="LLM returned empty response. Try a different model or check if the model is loaded.",
                    )

                return SummarizationResult(
                    success=True,
                    summary=summary.strip(),
                    model=model_used,
                )
            else:
                return SummarizationResult(
                    success=False,
                    error="No response from LLM",
                )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM summarization failed: {error_msg}")

            # Provide user-friendly error messages
            if "Connection refused" in error_msg:
                return SummarizationResult(
                    success=False,
                    error="Cannot connect to LLM server. Is it running?",
                )
            elif "timeout" in error_msg.lower():
                return SummarizationResult(
                    success=False,
                    error="LLM request timed out. Try again.",
                )

            return SummarizationResult(
                success=False,
                error=f"Summarization failed: {error_msg[:100]}",
            )


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp for summarized_at field."""
    return datetime.now(UTC)
