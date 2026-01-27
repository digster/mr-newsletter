"""Reusable dialog components with consistent styling."""

from typing import Callable, List, Optional

import flet as ft

from src.ui.components.gradient_color_picker import GradientColorPicker
from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors


class ConfirmDialog(ft.AlertDialog):
    """Confirmation dialog component with sophisticated styling."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        is_destructive: bool = False,
        page: Optional["ft.Page"] = None,
    ):
        colors = get_colors(page)

        super().__init__(
            title=ft.Text(
                title,
                size=Typography.H3_SIZE,
                weight=ft.FontWeight.W_600,
                color=colors.TEXT_PRIMARY,
            ),
            content=ft.Container(
                content=ft.Text(
                    message,
                    size=Typography.BODY_SIZE,
                    color=colors.TEXT_SECONDARY,
                ),
                padding=ft.padding.only(top=Spacing.SM),
            ),
            actions=[
                ft.TextButton(
                    cancel_text,
                    style=ft.ButtonStyle(
                        color=colors.TEXT_SECONDARY,
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                    ),
                    on_click=on_cancel,
                ),
                ft.ElevatedButton(
                    confirm_text,
                    bgcolor=colors.ERROR if is_destructive else colors.ACCENT,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                    ),
                    on_click=on_confirm,
                ),
            ],
            actions_padding=ft.padding.all(Spacing.MD),
            content_padding=ft.padding.symmetric(horizontal=Spacing.LG),
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG),
        )


class AddNewsletterDialog(ft.AlertDialog):
    """Dialog for adding a new newsletter with sophisticated styling."""

    def __init__(
        self,
        labels: List,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        page: Optional["ft.Page"] = None,
    ):
        colors = get_colors(page)

        self.name_field = ft.TextField(
            label="Newsletter Name",
            hint_text="e.g., Tech News",
            autofocus=True,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=colors.TEXT_SECONDARY,
            ),
            hint_style=ft.TextStyle(
                color=colors.TEXT_TERTIARY,
            ),
        )

        self.label_dropdown = ft.Dropdown(
            label="Gmail Label",
            hint_text="Select a Gmail label",
            options=[
                ft.dropdown.Option(key=label.id, text=label.name) for label in labels
            ],
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=colors.TEXT_SECONDARY,
            ),
            hint_style=ft.TextStyle(
                color=colors.TEXT_TERTIARY,
            ),
        )

        self.auto_fetch_switch = ft.Switch(
            label="Auto-fetch enabled",
            value=True,
            active_color=colors.ACCENT,
        )

        self.interval_field = ft.TextField(
            label="Fetch interval (minutes)",
            value="1440",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=colors.TEXT_SECONDARY,
            ),
        )

        self.color_picker = GradientColorPicker(colors=colors)

        super().__init__(
            title=ft.Text(
                "Add Newsletter",
                size=Typography.H3_SIZE,
                weight=ft.FontWeight.W_600,
                color=colors.TEXT_PRIMARY,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        self.name_field,
                        ft.Container(height=Spacing.SM),
                        self.label_dropdown,
                        ft.Container(height=Spacing.MD),
                        ft.Divider(height=1, color=colors.BORDER_SUBTLE),
                        ft.Container(height=Spacing.MD),
                        ft.Text(
                            "Auto-fetch settings",
                            size=Typography.CAPTION_SIZE,
                            weight=ft.FontWeight.W_500,
                            color=colors.TEXT_TERTIARY,
                        ),
                        ft.Container(height=Spacing.XS),
                        self.auto_fetch_switch,
                        ft.Container(height=Spacing.SM),
                        self.interval_field,
                        ft.Container(height=Spacing.MD),
                        ft.Divider(height=1, color=colors.BORDER_SUBTLE),
                        ft.Container(height=Spacing.MD),
                        self.color_picker,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
                padding=ft.padding.only(top=Spacing.SM),
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(
                        color=colors.TEXT_SECONDARY,
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                    ),
                    on_click=on_cancel,
                ),
                ft.ElevatedButton(
                    "Add Newsletter",
                    bgcolor=colors.ACCENT,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                    ),
                    on_click=on_save,
                ),
            ],
            actions_padding=ft.padding.all(Spacing.MD),
            content_padding=ft.padding.symmetric(horizontal=Spacing.LG),
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG),
        )

    def get_values(self) -> dict:
        """Get dialog field values."""
        color, color_secondary = self.color_picker.get_colors()
        return {
            "name": self.name_field.value,
            "label_id": self.label_dropdown.value,
            "auto_fetch": self.auto_fetch_switch.value,
            "interval": int(self.interval_field.value or "1440"),
            "color": color,
            "color_secondary": color_secondary,
        }


class EditNewsletterDialog(ft.AlertDialog):
    """Dialog for editing a newsletter with sophisticated styling."""

    def __init__(
        self,
        newsletter,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        page: Optional["ft.Page"] = None,
    ):
        self.newsletter = newsletter
        colors = get_colors(page)

        self.name_field = ft.TextField(
            label="Newsletter Name",
            value=newsletter.name,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=colors.TEXT_SECONDARY,
            ),
        )

        self.auto_fetch_switch = ft.Switch(
            label="Auto-fetch enabled",
            value=newsletter.auto_fetch_enabled,
            active_color=colors.ACCENT,
        )

        self.interval_field = ft.TextField(
            label="Fetch interval (minutes)",
            value=str(newsletter.fetch_interval_minutes or 1440),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=colors.TEXT_SECONDARY,
            ),
        )

        self.color_picker = GradientColorPicker(
            initial_color=newsletter.color,
            initial_color_secondary=newsletter.color_secondary,
            colors=colors,
        )

        super().__init__(
            title=ft.Text(
                "Edit Newsletter",
                size=Typography.H3_SIZE,
                weight=ft.FontWeight.W_600,
                color=colors.TEXT_PRIMARY,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Label info (read-only)
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.LABEL_OUTLINED,
                                        size=16,
                                        color=colors.TEXT_TERTIARY,
                                    ),
                                    ft.Container(width=Spacing.XS),
                                    ft.Text(
                                        newsletter.gmail_label_name,
                                        size=Typography.BODY_SMALL_SIZE,
                                        color=colors.TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                            bgcolor=colors.BG_TERTIARY,
                            padding=ft.padding.all(Spacing.SM),
                            border_radius=BorderRadius.SM,
                        ),
                        ft.Container(height=Spacing.MD),
                        self.name_field,
                        ft.Container(height=Spacing.MD),
                        ft.Divider(height=1, color=colors.BORDER_SUBTLE),
                        ft.Container(height=Spacing.MD),
                        ft.Text(
                            "Auto-fetch settings",
                            size=Typography.CAPTION_SIZE,
                            weight=ft.FontWeight.W_500,
                            color=colors.TEXT_TERTIARY,
                        ),
                        ft.Container(height=Spacing.XS),
                        self.auto_fetch_switch,
                        ft.Container(height=Spacing.SM),
                        self.interval_field,
                        ft.Container(height=Spacing.MD),
                        ft.Divider(height=1, color=colors.BORDER_SUBTLE),
                        ft.Container(height=Spacing.MD),
                        self.color_picker,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
                padding=ft.padding.only(top=Spacing.SM),
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(
                        color=colors.TEXT_SECONDARY,
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                    ),
                    on_click=on_cancel,
                ),
                ft.ElevatedButton(
                    "Save Changes",
                    bgcolor=colors.ACCENT,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                    ),
                    on_click=on_save,
                ),
            ],
            actions_padding=ft.padding.all(Spacing.MD),
            content_padding=ft.padding.symmetric(horizontal=Spacing.LG),
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG),
        )

    def get_values(self) -> dict:
        """Get dialog field values."""
        color, color_secondary = self.color_picker.get_colors()
        return {
            "name": self.name_field.value,
            "auto_fetch": self.auto_fetch_switch.value,
            "interval": int(self.interval_field.value or "1440"),
            "color": color,
            "color_secondary": color_secondary,
        }
