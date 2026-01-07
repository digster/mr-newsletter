"""Unit tests for EmailListItem component."""

import flet as ft
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.ui.components.email_list_item import EmailListItem


class TestEmailListItem:
    """Tests for EmailListItem component."""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing."""
        return datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_email_list_item_creates_with_required_props(self, sample_datetime):
        """Test item creation with minimum required properties."""
        item = EmailListItem(
            subject="Test Subject",
            sender="Test Sender",
            snippet="Test snippet...",
            received_at=sample_datetime,
        )
        assert item is not None
        assert isinstance(item, ft.Container)

    def test_email_list_item_stores_subject(self, sample_datetime):
        """Test subject is stored."""
        item = EmailListItem(
            subject="My Test Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.subject == "My Test Subject"

    def test_email_list_item_stores_sender(self, sample_datetime):
        """Test sender is stored."""
        item = EmailListItem(
            subject="Subject",
            sender="newsletter@example.com",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.sender == "newsletter@example.com"

    def test_email_list_item_stores_snippet(self, sample_datetime):
        """Test snippet is stored."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="This is a test snippet for the email...",
            received_at=sample_datetime,
        )
        assert item.snippet == "This is a test snippet for the email..."

    def test_email_list_item_stores_received_at(self, sample_datetime):
        """Test received_at is stored."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.received_at == sample_datetime

    def test_email_list_item_default_is_read_false(self, sample_datetime):
        """Test default is_read is False."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.is_read is False

    def test_email_list_item_default_is_starred_false(self, sample_datetime):
        """Test default is_starred is False."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.is_starred is False

    def test_email_list_item_unread_styling(self, sample_datetime):
        """Test unread email has SURFACE_CONTAINER background."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=False,
        )
        assert item.bgcolor == ft.Colors.SURFACE_CONTAINER

    def test_email_list_item_read_styling(self, sample_datetime):
        """Test read email has no background color."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=True,
        )
        assert item.bgcolor is None

    def test_email_list_item_starred_icon(self, sample_datetime):
        """Test starred email shows filled star icon."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_starred=True,
        )
        row = item.content
        star_button = row.controls[0]
        assert isinstance(star_button, ft.IconButton)
        assert star_button.icon == ft.Icons.STAR
        assert star_button.icon_color == ft.Colors.AMBER

    def test_email_list_item_unstarred_icon(self, sample_datetime):
        """Test unstarred email shows star outline icon."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_starred=False,
        )
        row = item.content
        star_button = row.controls[0]
        assert isinstance(star_button, ft.IconButton)
        assert star_button.icon == ft.Icons.STAR_BORDER
        assert star_button.icon_color is None

    def test_email_list_item_unread_indicator_visible(self, sample_datetime):
        """Test unread indicator is visible for unread emails."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=False,
        )
        row = item.content
        indicator = row.controls[1]
        assert isinstance(indicator, ft.Container)
        assert indicator.bgcolor == ft.Colors.PRIMARY

    def test_email_list_item_unread_indicator_hidden(self, sample_datetime):
        """Test unread indicator is hidden for read emails."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=True,
        )
        row = item.content
        indicator = row.controls[1]
        assert indicator.bgcolor is None

    def test_email_list_item_on_click_callback(self, sample_datetime):
        """Test click callback is set."""
        callback = MagicMock()
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            on_click=callback,
        )
        assert item.on_click == callback

    def test_email_list_item_on_star_callback(self, sample_datetime):
        """Test star button callback is set."""
        callback = MagicMock()
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            on_star=callback,
        )
        row = item.content
        star_button = row.controls[0]
        assert star_button.on_click == callback

    def test_email_list_item_date_formatting(self, sample_datetime):
        """Test date is formatted as 'Mon DD'."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        row = item.content
        date_text = row.controls[-1]
        assert isinstance(date_text, ft.Text)
        # June 15
        assert date_text.value == "Jun 15"

    def test_email_list_item_has_inkwell_effect(self, sample_datetime):
        """Test item has ink (ripple) effect."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.ink is True

    def test_email_list_item_border_radius(self, sample_datetime):
        """Test item has border radius."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.border_radius == 8

    def test_email_list_item_padding(self, sample_datetime):
        """Test item has proper padding."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.padding == 12

    def test_email_list_item_unread_subject_bold(self, sample_datetime):
        """Test unread email has bold subject."""
        item = EmailListItem(
            subject="Test Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=False,
        )
        row = item.content
        # Column with text is at index 3 (after star button, indicator, spacer)
        text_column = row.controls[3]
        subject_text = text_column.controls[0]
        assert subject_text.weight == ft.FontWeight.BOLD

    def test_email_list_item_read_subject_normal(self, sample_datetime):
        """Test read email has normal weight subject."""
        item = EmailListItem(
            subject="Test Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=True,
        )
        row = item.content
        text_column = row.controls[3]
        subject_text = text_column.controls[0]
        assert subject_text.weight == ft.FontWeight.NORMAL

    def test_email_list_item_subject_max_lines(self, sample_datetime):
        """Test subject text has max 1 line with ellipsis."""
        item = EmailListItem(
            subject="This is a very long subject that should be truncated",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        row = item.content
        text_column = row.controls[3]
        subject_text = text_column.controls[0]
        assert subject_text.max_lines == 1
        assert subject_text.overflow == ft.TextOverflow.ELLIPSIS

    def test_email_list_item_snippet_max_lines(self, sample_datetime):
        """Test snippet text has max 1 line with ellipsis."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="This is a very long snippet that should be truncated",
            received_at=sample_datetime,
        )
        row = item.content
        text_column = row.controls[3]
        snippet_text = text_column.controls[2]
        assert snippet_text.max_lines == 1
        assert snippet_text.overflow == ft.TextOverflow.ELLIPSIS
