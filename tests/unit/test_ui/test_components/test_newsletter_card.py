"""Unit tests for NewsletterCard component."""

import flet as ft
import pytest
from unittest.mock import MagicMock

from src.ui.components.newsletter_card import NewsletterCard
from src.ui.themes import BorderRadius, Colors, Spacing


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
        assert isinstance(card, ft.Container)

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
        """Test default accent color when none provided."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.accent_color == Colors.Light.ACCENT

    def test_newsletter_card_custom_color(self):
        """Test custom accent color is applied."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
            color="#FF5733",
        )
        assert card.accent_color == "#FF5733"

    def test_newsletter_card_has_content_column(self):
        """Test card has content wrapped in column."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.content is not None
        assert isinstance(card.content, ft.Column)

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
        assert card._on_click == callback

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
        assert card._on_refresh == callback

    def test_newsletter_card_has_title_in_header(self):
        """Test card has title in header row."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        column = card.content
        header_row = column.controls[0]
        # Title is the first control in header row
        title = header_row.controls[0]
        assert isinstance(title, ft.Text)
        assert title.value == "Newsletter"

    def test_newsletter_card_has_view_button(self):
        """Test card has View emails button container."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        column = card.content
        # View button is a Container with bgcolor (index 5 after header, subtitle, spacer, stats, spacer)
        view_button = column.controls[5]
        assert isinstance(view_button, ft.Container)
        assert view_button.bgcolor == Colors.Light.ACCENT_MUTED

    def test_newsletter_card_has_refresh_icon_button(self):
        """Test card has refresh IconButton."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        column = card.content
        actions_row = column.controls[-1]
        # Refresh button is the last control in actions row
        refresh_button = actions_row.controls[-1]
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
        """Test card has proper padding."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.padding == Spacing.SM

    def test_newsletter_card_has_border_radius(self):
        """Test card has proper border radius."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.border_radius == BorderRadius.MD

    def test_newsletter_card_has_border(self):
        """Test card has border."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.border is not None

    def test_newsletter_card_has_shadow(self):
        """Test card has shadow for depth."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.shadow is not None

    def test_newsletter_card_has_animation(self):
        """Test card has hover animation."""
        card = NewsletterCard(
            name="Newsletter",
            label="Label",
            unread_count=0,
            total_count=0,
        )
        assert card.animate is not None
