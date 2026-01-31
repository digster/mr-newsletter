"""Tests for LLMService - AI summarization.

These tests verify the LLM service correctly handles email summarization
with proper error handling and configuration resolution.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.llm_service import (
    LLMConfig,
    LLMService,
    SummarizationResult,
    get_current_timestamp,
)


class TestLLMServiceConfiguration:
    """Test LLM configuration resolution."""

    def test_is_enabled_from_settings(self):
        """Verify is_enabled reads from settings."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            assert service.is_enabled() is True

    def test_is_enabled_from_user_settings(self):
        """Verify user settings override env settings."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = False  # Env says disabled
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_user_settings = MagicMock()
        mock_user_settings.llm_enabled = True  # User says enabled
        mock_user_settings.llm_api_base_url = None
        mock_user_settings.llm_model = None
        mock_user_settings.llm_max_tokens = 500
        mock_user_settings.llm_temperature = 0.3
        mock_user_settings.llm_api_key_encrypted = None

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService(user_settings=mock_user_settings)
            assert service.is_enabled() is True


class TestLLMServiceConnection:
    """Test LLM connection checking."""

    @pytest.mark.asyncio
    async def test_check_connection_disabled(self):
        """Verify check_connection returns error when disabled."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = False
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            success, message = await service.check_connection()

            assert success is False
            assert "disabled" in message.lower()

    @pytest.mark.asyncio
    async def test_check_connection_success(self):
        """Verify check_connection returns success when connected."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_client = MagicMock()
        mock_client.models.list.return_value = [MagicMock(), MagicMock()]

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            success, message = await service.check_connection()

            assert success is True
            assert "connected" in message.lower()


class TestLLMServiceSummarization:
    """Test email summarization."""

    @pytest.mark.asyncio
    async def test_summarize_email_success(self):
        """Verify successful summarization returns result."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = "test-model"
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is the summary."
        mock_response.model = "test-model"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            result = await service.summarize_email(
                subject="Test Subject",
                body_text="This is the email body.",
            )

            assert result.success is True
            assert result.summary == "This is the summary."
            assert result.model == "test-model"

    @pytest.mark.asyncio
    async def test_summarize_email_disabled_returns_error(self):
        """Verify summarization when disabled returns error."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = False
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            result = await service.summarize_email(
                subject="Test",
                body_text="Body",
            )

            assert result.success is False
            assert "disabled" in result.error.lower()

    @pytest.mark.asyncio
    async def test_summarize_email_empty_body_error(self):
        """Verify empty body returns error."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = "test-model"
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            result = await service.summarize_email(
                subject="Test",
                body_text="",
            )

            assert result.success is False
            assert "no email content" in result.error.lower()

    @pytest.mark.asyncio
    async def test_summarize_email_handles_timeout(self):
        """Verify timeout error is handled gracefully."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = "test-model"
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection timeout")

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            result = await service.summarize_email(
                subject="Test",
                body_text="Body text",
            )

            assert result.success is False
            assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_summarize_email_cleans_think_tags(self):
        """Verify <think> tags from reasoning models are cleaned."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = "test-model"
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "<think>Let me reason about this...</think>This is the clean summary."
        )
        mock_response.model = "test-model"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            result = await service.summarize_email(
                subject="Test",
                body_text="Body text",
            )

            assert result.success is True
            assert "<think>" not in result.summary
            assert "This is the clean summary." == result.summary


class TestLLMServiceInputProcessing:
    """Test input processing and truncation."""

    def test_truncate_input_short_text(self):
        """Verify short text is not truncated."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            text = "Short text"
            result = service._truncate_input(text)

            assert result == text

    def test_truncate_input_long_text(self):
        """Verify long text is truncated with ellipsis."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            # Create very long text (over 8000 chars)
            text = "x" * 10000
            result = service._truncate_input(text)

            assert len(result) < len(text)
            assert "truncated" in result.lower()

    def test_clean_response_removes_think_tags(self):
        """Verify _clean_response removes <think> blocks."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        with patch("src.services.llm_service.get_settings", return_value=mock_settings):
            service = LLMService()
            text = "<think>Internal reasoning\nMultiple lines</think>Clean output"
            result = service._clean_response(text)

            assert result == "Clean output"


class TestLLMServiceModelDetection:
    """Test model auto-detection."""

    def test_get_available_model_returns_first(self):
        """Verify _get_available_model returns first model."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_model = MagicMock()
        mock_model.id = "local-model-1"

        mock_client = MagicMock()
        mock_client.models.list.return_value = [mock_model]

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            result = service._get_available_model()

            assert result == "local-model-1"

    def test_get_available_model_returns_none_on_error(self):
        """Verify _get_available_model returns None on error."""
        mock_settings = MagicMock()
        mock_settings.llm_enabled = True
        mock_settings.llm_api_base_url = "http://localhost:1234/v1"
        mock_settings.llm_api_key = ""
        mock_settings.llm_model = ""
        mock_settings.llm_max_tokens = 500
        mock_settings.llm_temperature = 0.3

        mock_client = MagicMock()
        mock_client.models.list.side_effect = Exception("Connection error")

        with patch("src.services.llm_service.get_settings", return_value=mock_settings), \
             patch("src.services.llm_service.OpenAI", return_value=mock_client):
            service = LLMService()
            result = service._get_available_model()

            assert result is None


class TestLLMServiceUtilities:
    """Test utility functions."""

    def test_get_current_timestamp_returns_utc(self):
        """Verify get_current_timestamp returns UTC datetime."""
        from datetime import UTC

        result = get_current_timestamp()

        assert result.tzinfo is not None
        # Check it's UTC-aware
        assert result.tzinfo == UTC

    def test_summarization_result_dataclass(self):
        """Verify SummarizationResult has expected fields."""
        result = SummarizationResult(
            success=True,
            summary="Test summary",
            model="test-model",
            error=None,
        )

        assert result.success is True
        assert result.summary == "Test summary"
        assert result.model == "test-model"
        assert result.error is None

    def test_llm_config_dataclass(self):
        """Verify LLMConfig has expected fields."""
        config = LLMConfig(
            enabled=True,
            api_base_url="http://localhost:1234/v1",
            api_key="test-key",
            model="test-model",
            max_tokens=500,
            temperature=0.3,
        )

        assert config.enabled is True
        assert config.api_base_url == "http://localhost:1234/v1"
        assert config.api_key == "test-key"
        assert config.model == "test-model"
        assert config.max_tokens == 500
        assert config.temperature == 0.3
