"""Unit tests for dialog components."""

import flet as ft
import pytest
from unittest.mock import MagicMock

from src.ui.components.dialogs import ConfirmDialog, AddNewsletterDialog
from tests.fixtures.sample_data import create_gmail_label


class TestConfirmDialog:
    """Tests for ConfirmDialog component."""

    def test_confirm_dialog_creates_with_required_props(self):
        """Test dialog creation with title and message."""
        dialog = ConfirmDialog(
            title="Confirm Action",
            message="Are you sure you want to proceed?",
        )
        assert dialog is not None
        assert isinstance(dialog, ft.AlertDialog)

    def test_confirm_dialog_title_is_set(self):
        """Test custom title is set."""
        dialog = ConfirmDialog(
            title="Delete Item",
            message="Message",
        )
        assert isinstance(dialog.title, ft.Text)
        assert dialog.title.value == "Delete Item"

    def test_confirm_dialog_message_is_set(self):
        """Test custom message is set."""
        dialog = ConfirmDialog(
            title="Title",
            message="This action cannot be undone.",
        )
        assert isinstance(dialog.content, ft.Text)
        assert dialog.content.value == "This action cannot be undone."

    def test_confirm_dialog_default_button_text(self):
        """Test default button text (Confirm/Cancel)."""
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
        )
        cancel_button = dialog.actions[0]
        confirm_button = dialog.actions[1]
        assert cancel_button.content == "Cancel"
        assert confirm_button.content == "Confirm"

    def test_confirm_dialog_custom_button_text(self):
        """Test custom button text."""
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
            confirm_text="Delete",
            cancel_text="Keep",
        )
        cancel_button = dialog.actions[0]
        confirm_button = dialog.actions[1]
        assert cancel_button.content == "Keep"
        assert confirm_button.content == "Delete"

    def test_confirm_dialog_destructive_styling(self):
        """Test destructive button has error color."""
        dialog = ConfirmDialog(
            title="Delete",
            message="This will delete the item permanently.",
            is_destructive=True,
        )
        confirm_button = dialog.actions[1]
        assert confirm_button.color == ft.Colors.ERROR

    def test_confirm_dialog_non_destructive_styling(self):
        """Test non-destructive button has no special color."""
        dialog = ConfirmDialog(
            title="Confirm",
            message="Confirm the action.",
            is_destructive=False,
        )
        confirm_button = dialog.actions[1]
        assert confirm_button.color is None

    def test_confirm_dialog_on_confirm_callback(self):
        """Test confirm button callback is set."""
        callback = MagicMock()
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
            on_confirm=callback,
        )
        confirm_button = dialog.actions[1]
        assert confirm_button.on_click == callback

    def test_confirm_dialog_on_cancel_callback(self):
        """Test cancel button callback is set."""
        callback = MagicMock()
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
            on_cancel=callback,
        )
        cancel_button = dialog.actions[0]
        assert cancel_button.on_click == callback

    def test_confirm_dialog_has_two_action_buttons(self):
        """Test dialog has exactly two action buttons."""
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
        )
        assert len(dialog.actions) == 2

    def test_confirm_dialog_cancel_is_text_button(self):
        """Test cancel button is TextButton."""
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
        )
        cancel_button = dialog.actions[0]
        assert isinstance(cancel_button, ft.TextButton)

    def test_confirm_dialog_confirm_is_elevated_button(self):
        """Test confirm button is ElevatedButton."""
        dialog = ConfirmDialog(
            title="Title",
            message="Message",
        )
        confirm_button = dialog.actions[1]
        assert isinstance(confirm_button, ft.ElevatedButton)


class TestAddNewsletterDialog:
    """Tests for AddNewsletterDialog component."""

    @pytest.fixture
    def sample_labels(self):
        """Create sample Gmail labels for testing."""
        return [
            create_gmail_label(id="Label_1", name="Newsletters/Tech"),
            create_gmail_label(id="Label_2", name="Newsletters/Finance"),
            create_gmail_label(id="Label_3", name="Newsletters/News"),
        ]

    def test_add_newsletter_dialog_creates_with_labels(self, sample_labels):
        """Test dialog creation with label options."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog is not None
        assert isinstance(dialog, ft.AlertDialog)

    def test_add_newsletter_dialog_title(self, sample_labels):
        """Test dialog has correct title."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert isinstance(dialog.title, ft.Text)
        assert dialog.title.value == "Add Newsletter"

    def test_add_newsletter_dialog_name_field_exists(self, sample_labels):
        """Test name TextField is present."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.name_field is not None
        assert isinstance(dialog.name_field, ft.TextField)
        assert dialog.name_field.label == "Newsletter Name"

    def test_add_newsletter_dialog_name_field_has_hint(self, sample_labels):
        """Test name field has hint text."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.name_field.hint_text == "e.g., Tech News"

    def test_add_newsletter_dialog_name_field_autofocus(self, sample_labels):
        """Test name field has autofocus."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.name_field.autofocus is True

    def test_add_newsletter_dialog_label_dropdown_exists(self, sample_labels):
        """Test Gmail label Dropdown is present."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.label_dropdown is not None
        assert isinstance(dialog.label_dropdown, ft.Dropdown)
        assert dialog.label_dropdown.label == "Gmail Label"

    def test_add_newsletter_dialog_label_dropdown_options(self, sample_labels):
        """Test label dropdown has correct options."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        options = dialog.label_dropdown.options
        assert len(options) == 3
        assert options[0].key == "Label_1"
        assert options[0].text == "Newsletters/Tech"
        assert options[1].key == "Label_2"
        assert options[1].text == "Newsletters/Finance"

    def test_add_newsletter_dialog_auto_fetch_switch_exists(self, sample_labels):
        """Test auto-fetch Switch is present."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.auto_fetch_switch is not None
        assert isinstance(dialog.auto_fetch_switch, ft.Switch)
        assert dialog.auto_fetch_switch.label == "Auto-fetch enabled"

    def test_add_newsletter_dialog_auto_fetch_default_on(self, sample_labels):
        """Test auto-fetch switch is on by default."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.auto_fetch_switch.value is True

    def test_add_newsletter_dialog_interval_field_exists(self, sample_labels):
        """Test fetch interval TextField is present."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.interval_field is not None
        assert isinstance(dialog.interval_field, ft.TextField)
        assert dialog.interval_field.label == "Fetch interval (minutes)"

    def test_add_newsletter_dialog_interval_default_value(self, sample_labels):
        """Test default fetch interval is 1440 (24 hours)."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.interval_field.value == "1440"

    def test_add_newsletter_dialog_interval_keyboard_type(self, sample_labels):
        """Test interval field has number keyboard."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert dialog.interval_field.keyboard_type == ft.KeyboardType.NUMBER

    def test_add_newsletter_dialog_get_values(self, sample_labels):
        """Test get_values returns correct dict."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        dialog.name_field.value = "My Newsletter"
        dialog.label_dropdown.value = "Label_2"
        dialog.auto_fetch_switch.value = False
        dialog.interval_field.value = "60"

        values = dialog.get_values()
        assert values["name"] == "My Newsletter"
        assert values["label_id"] == "Label_2"
        assert values["auto_fetch"] is False
        assert values["interval"] == 60

    def test_add_newsletter_dialog_get_values_default_interval(self, sample_labels):
        """Test get_values uses 1440 for empty interval."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        dialog.name_field.value = "Test"
        dialog.interval_field.value = ""

        values = dialog.get_values()
        assert values["interval"] == 1440

    def test_add_newsletter_dialog_on_save_callback(self, sample_labels):
        """Test Add button callback is set."""
        callback = MagicMock()
        dialog = AddNewsletterDialog(labels=sample_labels, on_save=callback)
        add_button = dialog.actions[1]
        assert add_button.on_click == callback

    def test_add_newsletter_dialog_on_cancel_callback(self, sample_labels):
        """Test Cancel button callback is set."""
        callback = MagicMock()
        dialog = AddNewsletterDialog(labels=sample_labels, on_cancel=callback)
        cancel_button = dialog.actions[0]
        assert cancel_button.on_click == callback

    def test_add_newsletter_dialog_has_two_action_buttons(self, sample_labels):
        """Test dialog has exactly two action buttons."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        assert len(dialog.actions) == 2

    def test_add_newsletter_dialog_button_text(self, sample_labels):
        """Test button text is Cancel and Add."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        cancel_button = dialog.actions[0]
        add_button = dialog.actions[1]
        assert cancel_button.content == "Cancel"
        assert add_button.content == "Add"

    def test_add_newsletter_dialog_content_width(self, sample_labels):
        """Test content column has 400px width."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        content_column = dialog.content
        assert content_column.width == 400

    def test_add_newsletter_dialog_content_is_tight(self, sample_labels):
        """Test content column is tight (no extra spacing)."""
        dialog = AddNewsletterDialog(labels=sample_labels)
        content_column = dialog.content
        assert content_column.tight is True

    def test_add_newsletter_dialog_with_empty_labels(self):
        """Test dialog handles empty labels list."""
        dialog = AddNewsletterDialog(labels=[])
        assert dialog is not None
        assert len(dialog.label_dropdown.options) == 0
