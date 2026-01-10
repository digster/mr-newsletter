"""Unit tests for EmailListItem component."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import flet as ft
import pytest

from src.ui.components.email_list_item import EmailListItem
from src.ui.themes import BorderRadius, Colors, Spacing


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
        """Test unread email has secondary background."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=False,
        )
        assert item.bgcolor == Colors.Light.BG_SECONDARY

    def test_email_list_item_read_styling(self, sample_datetime):
        """Test read email has primary background color."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            is_read=True,
        )
        assert item.bgcolor == Colors.Light.BG_PRIMARY

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
        # Star container is at index 2 (unread dot, spacer, star container)
        star_container = row.controls[2]
        star_icon = star_container.content
        assert isinstance(star_icon, ft.Icon)
        # Icon is starred - check color
        assert star_icon.color == Colors.Light.STAR_ACTIVE

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
        star_container = row.controls[2]
        star_icon = star_container.content
        assert isinstance(star_icon, ft.Icon)
        # Icon uses 'src' attribute in newer Flet
        assert star_icon.color == Colors.Light.STAR_INACTIVE

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
        # Unread indicator is the first container
        indicator = row.controls[0]
        assert isinstance(indicator, ft.Container)
        assert indicator.bgcolor == Colors.Light.UNREAD_DOT

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
        indicator = row.controls[0]
        assert indicator.bgcolor is None

    def test_email_list_item_on_click_callback(self, sample_datetime):
        """Test click callback is stored."""
        callback = MagicMock()
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            on_click=callback,
        )
        assert item._on_click == callback

    def test_email_list_item_on_star_callback(self, sample_datetime):
        """Test star button callback is stored."""
        callback = MagicMock()
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
            on_star=callback,
        )
        assert item._on_star == callback

    def test_email_list_item_date_formatting(self):
        """Test date is formatted correctly based on recency."""
        from datetime import date, timedelta

        # Use a date more than 7 days ago to test month/day format
        today = date.today()
        test_date = today - timedelta(days=30)  # 30 days ago
        test_datetime = datetime(
            test_date.year, test_date.month, test_date.day, 10, 30, 0, tzinfo=timezone.utc
        )

        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=test_datetime,
        )
        row = item.content
        date_text = row.controls[-1]
        assert isinstance(date_text, ft.Text)
        # Date formatting based on recency:
        # - Same year: "Mon DD" format
        # - Different year: "Mon DD, YYYY" format
        if test_date.year == today.year:
            expected = test_datetime.strftime("%b %d")
        else:
            expected = test_datetime.strftime("%b %d, %Y")
        assert date_text.value == expected

    def test_email_list_item_border_radius(self, sample_datetime):
        """Test item has border radius from design tokens."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.border_radius == BorderRadius.SM

    def test_email_list_item_padding(self, sample_datetime):
        """Test item has proper padding from design tokens."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        # Uses symmetric padding
        assert item.padding is not None

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
        # Column with text is at index 4 (unread dot, spacer, star container, spacer, column)
        text_column = row.controls[4]
        subject_text = text_column.controls[0]
        assert subject_text.weight == ft.FontWeight.W_500

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
        text_column = row.controls[4]
        subject_text = text_column.controls[0]
        assert subject_text.weight == ft.FontWeight.W_400

    def test_email_list_item_subject_max_lines(self, sample_datetime):
        """Test subject text has max 1 line with ellipsis."""
        item = EmailListItem(
            subject="This is a very long subject that should be truncated",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        row = item.content
        text_column = row.controls[4]
        subject_text = text_column.controls[0]
        assert subject_text.max_lines == 1
        assert subject_text.overflow == ft.TextOverflow.ELLIPSIS

    def test_email_list_item_has_hover_animation(self, sample_datetime):
        """Test item has animation for hover states."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.animate is not None

    def test_email_list_item_has_border(self, sample_datetime):
        """Test item has bottom border."""
        item = EmailListItem(
            subject="Subject",
            sender="Sender",
            snippet="Snippet",
            received_at=sample_datetime,
        )
        assert item.border is not None
