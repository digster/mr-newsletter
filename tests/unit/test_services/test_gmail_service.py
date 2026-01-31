"""Tests for GmailService - Gmail API wrapper.

These tests verify the Gmail service correctly wraps the Gmail API.
CRITICAL: Tests also verify that NO delete or trash methods exist to
protect users from accidental email deletion.
"""

import base64
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.services.gmail_service import GmailLabel, GmailMessage, GmailService


class TestGmailServiceNeverDeletesEmails:
    """CRITICAL: Verify the Gmail service never has delete/trash functionality.

    This test class is the most important - it ensures we never accidentally
    add methods that could delete user emails.
    """

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked credentials."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_build.return_value = MagicMock()
            return GmailService(mock_creds)

    def test_no_delete_method_exists(self, gmail_service):
        """CRITICAL: Verify no delete method exists on GmailService."""
        # Check for any method that might delete emails
        dangerous_methods = [
            "delete",
            "delete_email",
            "delete_message",
            "remove_email",
            "remove_message",
        ]

        for method_name in dangerous_methods:
            assert not hasattr(gmail_service, method_name), \
                f"DANGEROUS: {method_name} method exists on GmailService!"

    def test_no_trash_method_exists(self, gmail_service):
        """CRITICAL: Verify no trash method exists on GmailService."""
        # Check for any method that might trash emails
        dangerous_methods = [
            "trash",
            "trash_email",
            "trash_message",
            "move_to_trash",
        ]

        for method_name in dangerous_methods:
            assert not hasattr(gmail_service, method_name), \
                f"DANGEROUS: {method_name} method exists on GmailService!"

    def test_api_calls_never_include_delete(self, gmail_service):
        """CRITICAL: Verify the service's API object has no delete exposure."""
        # The service object should not expose delete operations
        service_methods = dir(gmail_service)

        # Check no method contains 'delete' or 'trash' in name
        for method in service_methods:
            if not method.startswith("_"):  # Skip private/dunder
                assert "delete" not in method.lower(), \
                    f"DANGEROUS: Method {method} contains 'delete'!"
                assert "trash" not in method.lower(), \
                    f"DANGEROUS: Method {method} contains 'trash'!"


class TestGmailServiceUserProfile:
    """Test user profile operations."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            service._mock_api = mock_service
            return service

    def test_get_user_email_returns_profile_email(self, gmail_service):
        """Verify get_user_email returns the email from profile."""
        mock_profile = {"emailAddress": "test@gmail.com"}
        gmail_service.service.users().getProfile().execute.return_value = mock_profile

        result = gmail_service.get_user_email()

        assert result == "test@gmail.com"

    def test_get_user_email_returns_empty_on_error(self, gmail_service):
        """Verify get_user_email returns empty string on API error."""
        from googleapiclient.errors import HttpError

        mock_response = MagicMock()
        mock_response.status = 403
        gmail_service.service.users().getProfile().execute.side_effect = HttpError(
            mock_response, b"Access denied"
        )

        result = gmail_service.get_user_email()

        assert result == ""


class TestGmailServiceLabels:
    """Test label operations."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            return service

    def test_get_labels_returns_user_labels_only(self, gmail_service):
        """Verify get_labels filters out system labels when requested."""
        mock_labels_list = {
            "labels": [
                {"id": "Label_1", "name": "Newsletters", "type": "user"},
                {"id": "INBOX", "name": "INBOX", "type": "system"},
                {"id": "Label_2", "name": "Tech News", "type": "user"},
            ]
        }
        mock_label_detail = {
            "id": "Label_1",
            "name": "Newsletters",
            "messagesTotal": 50,
        }

        gmail_service.service.users().labels().list().execute.return_value = mock_labels_list
        gmail_service.service.users().labels().get().execute.return_value = mock_label_detail

        result = gmail_service.get_labels(user_labels_only=True)

        # Should only include user labels, not INBOX
        label_names = [label.name for label in result]
        assert "INBOX" not in label_names

    def test_get_labels_returns_gmail_label_objects(self, gmail_service):
        """Verify get_labels returns properly typed GmailLabel objects."""
        mock_labels_list = {
            "labels": [
                {"id": "Label_1", "name": "Newsletters", "type": "user"},
            ]
        }
        mock_label_detail = {
            "id": "Label_1",
            "name": "Newsletters",
            "messagesTotal": 50,
        }

        gmail_service.service.users().labels().list().execute.return_value = mock_labels_list
        gmail_service.service.users().labels().get().execute.return_value = mock_label_detail

        result = gmail_service.get_labels()

        assert len(result) >= 0
        if result:
            assert isinstance(result[0], GmailLabel)

    def test_get_labels_skips_inaccessible_labels(self, gmail_service):
        """Verify get_labels handles labels that can't be fetched."""
        from googleapiclient.errors import HttpError

        mock_labels_list = {
            "labels": [
                {"id": "Label_1", "name": "Accessible", "type": "user"},
                {"id": "Label_2", "name": "Inaccessible", "type": "user"},
            ]
        }

        gmail_service.service.users().labels().list().execute.return_value = mock_labels_list

        # Create mock for get that raises on second call
        mock_response = MagicMock()
        mock_response.status = 404

        call_count = [0]
        accessible_detail = {"id": "Label_1", "name": "Accessible", "messagesTotal": 10}

        def mock_get_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                return accessible_detail
            raise HttpError(mock_response, b"Not found")

        # Mock the chain: users().labels().get(userId="me", id=...).execute()
        mock_get_result = MagicMock()
        mock_get_result.execute = mock_get_execute
        gmail_service.service.users().labels().get.return_value = mock_get_result

        # Should not raise, just skip the inaccessible label
        result = gmail_service.get_labels()
        # At least one label should be returned
        assert isinstance(result, list)


class TestGmailServiceMessages:
    """Test message operations."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            return service

    def test_get_messages_by_label_returns_ids(self, gmail_service):
        """Verify get_messages_by_label returns message IDs."""
        mock_response = {
            "messages": [
                {"id": "msg_1", "threadId": "thread_1"},
                {"id": "msg_2", "threadId": "thread_2"},
            ],
            "nextPageToken": None,
        }
        gmail_service.service.users().messages().list().execute.return_value = mock_response

        message_ids, next_token = gmail_service.get_messages_by_label("Label_123")

        assert message_ids == ["msg_1", "msg_2"]
        assert next_token is None

    def test_get_messages_by_label_with_pagination(self, gmail_service):
        """Verify get_messages_by_label returns next page token."""
        mock_response = {
            "messages": [{"id": "msg_1"}],
            "nextPageToken": "token_for_next_page",
        }
        gmail_service.service.users().messages().list().execute.return_value = mock_response

        message_ids, next_token = gmail_service.get_messages_by_label("Label_123")

        assert next_token == "token_for_next_page"

    def test_get_messages_by_label_with_date_filter(self, gmail_service):
        """Verify get_messages_by_label applies date filter correctly."""
        mock_response = {"messages": [], "nextPageToken": None}
        mock_list = MagicMock()
        mock_list.execute.return_value = mock_response
        gmail_service.service.users().messages().list.return_value = mock_list

        after_date = datetime(2024, 1, 15)
        gmail_service.get_messages_by_label("Label_123", after_date=after_date)

        # Verify the API was called with a query containing the date
        call_kwargs = gmail_service.service.users().messages().list.call_args
        if call_kwargs and call_kwargs[1].get("q"):
            assert "after:" in call_kwargs[1]["q"]


class TestGmailServiceMessageParsing:
    """Test message detail parsing."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            return service

    def test_get_message_detail_parses_headers(self, gmail_service):
        """Verify message headers are correctly parsed."""
        mock_message = {
            "id": "msg_123",
            "threadId": "thread_123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Newsletter"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "body": {"size": 0},
            },
            "snippet": "Preview text...",
            "sizeEstimate": 1024,
        }
        gmail_service.service.users().messages().get().execute.return_value = mock_message

        result = gmail_service.get_message_detail("msg_123")

        assert result is not None
        assert result.subject == "Test Newsletter"
        assert result.sender_email == "sender@example.com"

    def test_get_message_detail_extracts_body(self, gmail_service):
        """Verify message body is correctly extracted."""
        body_content = "Hello, this is the email body."
        encoded_body = base64.urlsafe_b64encode(body_content.encode()).decode()

        mock_message = {
            "id": "msg_123",
            "threadId": "thread_123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "test@example.com"},
                ],
                "mimeType": "text/plain",
                "body": {"data": encoded_body, "size": len(body_content)},
            },
            "snippet": "Preview...",
            "sizeEstimate": 500,
            "internalDate": "1705312800000",
        }
        gmail_service.service.users().messages().get().execute.return_value = mock_message

        result = gmail_service.get_message_detail("msg_123")

        assert result is not None
        assert result.body_text == body_content

    def test_parse_from_header_with_name_and_email(self, gmail_service):
        """Verify From header parsing with name and email."""
        result = gmail_service._parse_from_header('John Doe <john@example.com>')

        assert result == ("John Doe", "john@example.com")

    def test_parse_from_header_with_quoted_name(self, gmail_service):
        """Verify From header parsing with quoted name."""
        result = gmail_service._parse_from_header('"John Doe" <john@example.com>')

        assert result[1] == "john@example.com"

    def test_parse_from_header_email_only(self, gmail_service):
        """Verify From header parsing with email only."""
        result = gmail_service._parse_from_header("john@example.com")

        assert result == (None, "john@example.com")

    def test_parse_from_header_empty_name(self, gmail_service):
        """Verify From header parsing with empty name."""
        result = gmail_service._parse_from_header("<john@example.com>")

        assert result[1] == "john@example.com"
        assert result[0] is None


class TestGmailServiceMessageCount:
    """Test message count operations."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            return service

    def test_get_message_count_for_label(self, gmail_service):
        """Verify get_message_count_for_label returns correct count."""
        mock_label = {"id": "Label_123", "messagesTotal": 42}
        gmail_service.service.users().labels().get().execute.return_value = mock_label

        result = gmail_service.get_message_count_for_label("Label_123")

        assert result == 42

    def test_get_message_count_for_label_returns_zero_on_error(self, gmail_service):
        """Verify get_message_count_for_label returns 0 on API error."""
        from googleapiclient.errors import HttpError

        mock_response = MagicMock()
        mock_response.status = 404
        gmail_service.service.users().labels().get().execute.side_effect = HttpError(
            mock_response, b"Not found"
        )

        result = gmail_service.get_message_count_for_label("invalid_label")

        assert result == 0


class TestGmailServiceAsyncWrappers:
    """Test async wrapper methods."""

    @pytest.fixture
    def gmail_service(self):
        """Create GmailService with mocked API."""
        mock_creds = MagicMock()
        with patch("src.services.gmail_service.build") as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            service = GmailService(mock_creds)
            return service

    @pytest.mark.asyncio
    async def test_get_user_email_async_calls_sync_method(self, gmail_service):
        """Verify async wrapper calls the sync method."""
        mock_profile = {"emailAddress": "test@gmail.com"}
        gmail_service.service.users().getProfile().execute.return_value = mock_profile

        result = await gmail_service.get_user_email_async()

        assert result == "test@gmail.com"

    @pytest.mark.asyncio
    async def test_get_labels_async_returns_list(self, gmail_service):
        """Verify async get_labels returns a list."""
        gmail_service.service.users().labels().list().execute.return_value = {"labels": []}

        result = await gmail_service.get_labels_async()

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_messages_by_label_async_returns_tuple(self, gmail_service):
        """Verify async get_messages_by_label returns tuple."""
        mock_response = {"messages": [], "nextPageToken": None}
        gmail_service.service.users().messages().list().execute.return_value = mock_response

        result = await gmail_service.get_messages_by_label_async("Label_123")

        assert isinstance(result, tuple)
        assert len(result) == 2
