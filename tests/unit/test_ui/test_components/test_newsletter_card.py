"""Unit tests for NewsletterCard component."""

import flet as ft
import pytest
from unittest.mock import MagicMock

from src.ui.components.newsletter_card import NewsletterCard


class TestNewsletterCard:
    """Tests for NewsletterCard component."""

    def test_newsletter_card_creates_with_required_props(self):
        """Test card creation with minimum required properties."""
        card = NewsletterCard(
            name="Test Newsletter",
            label="Test Label",
            unread_count=5,
            total_count=25,
        )
        assert card is not None
        assert isinstance(card, ft.Card)

    def test_newsletter_card_stores_name(self):
        """Test newsletter name is stored."""
        card = NewsletterCard(
            name="My Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.name == "My Newsletter"

    def test_newsletter_card_stores_label(self):
        """Test Gmail label is stored."""
        card = NewsletterCard(
            name="Newsletter",
            label="Newsletters/Tech",
            unread_count=0,
            total_count=0,
        )
        assert card.label == "Newsletters/Tech"

    def test_newsletter_card_stores_unread_count(self):
        """Test unread count is stored."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=10,
            total_count=50,
        )
        assert card.unread_count == 10

    def test_newsletter_card_stores_total_count(self):
        """Test total count is stored."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=5,
            total_count=100,
        )
        assert card.total_count == 100

    def test_newsletter_card_default_color(self):
        """Test default color when none provided."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.color == "#6750A4"

    def test_newsletter_card_custom_color(self):
        """Test custom color is applied."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
            color="#FF5733",
        )
        assert card.color == "#FF5733"

    def test_newsletter_card_has_content_container(self):
        """Test card has content wrapped in container."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.content is not None
        assert isinstance(card.content, ft.Container)

    def test_newsletter_card_on_click_callback_set(self):
        """Test View button click callback is set."""
        callback = MagicMock()
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
            on_click=callback,
        )
        # Find the TextButton in the card content
        container = card.content
        column = container.content
        # The last row contains the buttons
        button_row = column.controls[-1]
        view_button = button_row.controls[0]
        assert view_button.on_click == callback

    def test_newsletter_card_on_refresh_callback_set(self):
        """Test refresh button click callback is set."""
        callback = MagicMock()
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
            on_refresh=callback,
        )
        # Find the IconButton in the card content
        container = card.content
        column = container.content
        button_row = column.controls[-1]
        refresh_button = button_row.controls[1]
        assert refresh_button.on_click == callback

    def test_newsletter_card_has_email_icon(self):
        """Test card has email icon."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        container = card.content
        column = container.content
        header_row = column.controls[0]
        icon_container = header_row.controls[0]
        icon = icon_container.content
        assert isinstance(icon, ft.Icon)

    def test_newsletter_card_has_view_button(self):
        """Test card has View button."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        container = card.content
        column = container.content
        button_row = column.controls[-1]
        view_button = button_row.controls[0]
        assert isinstance(view_button, ft.TextButton)
        assert view_button.content == "View"

    def test_newsletter_card_has_refresh_icon_button(self):
        """Test card has refresh IconButton."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        container = card.content
        column = container.content
        button_row = column.controls[-1]
        refresh_button = button_row.controls[1]
        assert isinstance(refresh_button, ft.IconButton)
        assert refresh_button.icon == ft.Icons.REFRESH

    def test_newsletter_card_with_zero_counts(self):
        """Test card handles zero counts correctly."""
        card = NewsletterCard(
            name="Empty Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.unread_count == 0
        assert card.total_count == 0

    def test_newsletter_card_with_large_counts(self):
        """Test card handles large counts correctly."""
        card = NewsletterCard(
            name="Popular Newsletter",
            label="Label",
            unread_count=999,
            total_count=9999,
        )
        assert card.unread_count == 999
        assert card.total_count == 9999

    def test_newsletter_card_content_padding(self):
        """Test card content has proper padding."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        container = card.content
        assert container.padding == 16
