"""Reusable dialog components."""

import flet as ft


class ConfirmDialog(ft.AlertDialog):
    """Confirmation dialog component."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm=None,
        on_cancel=None,
        is_destructive: bool = False,
    ):
        super().__init__(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(cancel_text, on_click=on_cancel),
                ft.ElevatedButton(
                    confirm_text,
                    color=ft.colors.ERROR if is_destructive else None,
                    on_click=on_confirm,
                ),
            ],
        )


class AddNewsletterDialog(ft.AlertDialog):
    """Dialog for adding a new newsletter."""

    def __init__(
        self,
        labels: list,
        on_save=None,
        on_cancel=None,
    ):
        self.name_field = ft.TextField(
            label="Newsletter Name",
            hint_text="e.g., Tech News",
            autofocus=True,
        )

        self.label_dropdown = ft.Dropdown(
            label="Gmail Label",
            hint_text="Select a Gmail label",
            options=[
                ft.dropdown.Option(key=label.id, text=label.name) for label in labels
            ],
        )

        self.auto_fetch_switch = ft.Switch(
            label="Auto-fetch enabled",
            value=True,
        )

        self.interval_field = ft.TextField(
            label="Fetch interval (minutes)",
            value="1440",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        super().__init__(
            title=ft.Text("Add Newsletter"),
            content=ft.Column(
                [
                    self.name_field,
                    ft.Container(height=8),
                    self.label_dropdown,
                    ft.Container(height=8),
                    self.auto_fetch_switch,
                    ft.Container(height=8),
                    self.interval_field,
                ],
                tight=True,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.ElevatedButton("Add", on_click=on_save),
            ],
        )

    def get_values(self) -> dict:
        """Get dialog field values."""
        return {
            "name": self.name_field.value,
            "label_id": self.label_dropdown.value,
            "auto_fetch": self.auto_fetch_switch.value,
            "interval": int(self.interval_field.value or "1440"),
        }
