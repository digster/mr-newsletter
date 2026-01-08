"""Newsletters management page."""

from typing import TYPE_CHECKING, Optional

import flet as ft

from src.services.gmail_service import GmailLabel
from src.services.newsletter_service import NewsletterService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class NewslettersPage(ft.View):
    """Page for managing newsletters."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/newsletters")
        self.app = app

        self.newsletters_list = ft.ListView(
            expand=True,
            spacing=8,
        )
        self.loading = ft.ProgressRing(visible=False)

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: self.app.navigate("/home"),
            ),
            title=ft.Text("Manage Newsletters"),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="Add newsletter",
                    on_click=lambda e: self.app.page.run_task(self._show_add_dialog, e),
                ),
            ],
        )

        self.controls = [self._build_content()]

        # Load newsletters
        self.app.page.run_task(self._load_newsletters)

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Your Newsletters",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            self.loading,
                        ],
                    ),
                    ft.Container(height=16),
                    self.newsletters_list,
                ],
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    async def _load_newsletters(self) -> None:
        """Load newsletters from database."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                service = NewsletterService(session=session)
                newsletters = await service.get_all_newsletters()

            self.newsletters_list.controls.clear()

            for newsletter in newsletters:
                tile = self._create_newsletter_tile(newsletter)
                self.newsletters_list.controls.append(tile)

            if not newsletters:
                self.newsletters_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "No newsletters yet. Click + to add one.",
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        padding=24,
                    )
                )

        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_newsletter_tile(self, newsletter) -> ft.Control:
        """Create a list tile for a newsletter."""
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.EMAIL,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=newsletter.color or "#6750A4",
                            border_radius=8,
                            padding=12,
                        ),
                        ft.Container(width=16),
                        ft.Column(
                            [
                                ft.Text(
                                    newsletter.name,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Label: {newsletter.gmail_label_name}",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Text(
                                    f"Auto-fetch: {'Every ' + str(newsletter.fetch_interval_minutes) + ' min' if newsletter.auto_fetch_enabled else 'Disabled'}",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Edit",
                            on_click=lambda _, n=newsletter: self._show_edit_dialog(n),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Delete",
                            on_click=lambda _, n=newsletter: self._confirm_delete(n),
                        ),
                    ],
                ),
                padding=16,
            ),
        )

    async def _show_add_dialog(self, e: ft.ControlEvent) -> None:
        """Show dialog to add a newsletter."""
        # Get labels from Gmail
        if not self.app.gmail_service:
            self.app.show_snackbar("Not authenticated", error=True)
            return

        labels = self.app.gmail_service.get_labels(user_labels_only=True)

        # Create dialog
        name_field = ft.TextField(
            label="Newsletter Name",
            hint_text="e.g., Tech News",
            autofocus=True,
        )

        label_dropdown = ft.Dropdown(
            label="Gmail Label",
            hint_text="Select a Gmail label",
            options=[
                ft.dropdown.Option(key=label.id, text=label.name) for label in labels
            ],
        )

        auto_fetch_switch = ft.Switch(label="Auto-fetch enabled", value=True)

        interval_field = ft.TextField(
            label="Fetch interval (minutes)",
            value="1440",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        async def save_newsletter(e: ft.ControlEvent) -> None:
            name = name_field.value.strip()
            label_id = label_dropdown.value

            if not name:
                self.app.show_snackbar("Name is required", error=True)
                return
            if not label_id:
                self.app.show_snackbar("Label is required", error=True)
                return

            # Find label name
            label_name = next(
                (l.name for l in labels if l.id == label_id), label_id
            )

            try:
                interval = int(interval_field.value or "1440")
            except ValueError:
                interval = 1440

            try:
                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)

                    # Check if label already used
                    if await service.label_exists(label_id):
                        self.app.show_snackbar(
                            "A newsletter with this label already exists",
                            error=True,
                        )
                        return

                    await service.create_newsletter(
                        name=name,
                        gmail_label_id=label_id,
                        gmail_label_name=label_name,
                        auto_fetch=auto_fetch_switch.value,
                        fetch_interval=interval,
                    )

                self.app.page.pop_dialog(dialog)
                self.app.show_snackbar(f"Newsletter '{name}' created")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Add Newsletter"),
            content=ft.Column(
                [
                    name_field,
                    ft.Container(height=8),
                    label_dropdown,
                    ft.Container(height=8),
                    auto_fetch_switch,
                    ft.Container(height=8),
                    interval_field,
                ],
                tight=True,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.app.page.pop_dialog(dialog)),
                ft.ElevatedButton("Add", on_click=lambda e: self.app.page.run_task(save_newsletter, e)),
            ],
        )

        self.app.page.show_dialog(dialog)

    def _show_edit_dialog(self, newsletter) -> None:
        """Show dialog to edit a newsletter."""
        name_field = ft.TextField(
            label="Newsletter Name",
            value=newsletter.name,
        )

        auto_fetch_switch = ft.Switch(
            label="Auto-fetch enabled",
            value=newsletter.auto_fetch_enabled,
        )

        interval_field = ft.TextField(
            label="Fetch interval (minutes)",
            value=str(newsletter.fetch_interval_minutes),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        async def save_changes(e: ft.ControlEvent) -> None:
            name = name_field.value.strip()
            if not name:
                self.app.show_snackbar("Name is required", error=True)
                return

            try:
                interval = int(interval_field.value or "1440")
            except ValueError:
                interval = 1440

            try:
                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)
                    await service.update_newsletter(
                        newsletter_id=newsletter.id,
                        name=name,
                        auto_fetch=auto_fetch_switch.value,
                        fetch_interval=interval,
                    )

                self.app.page.pop_dialog(dialog)
                self.app.show_snackbar("Newsletter updated")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Newsletter"),
            content=ft.Column(
                [
                    name_field,
                    ft.Container(height=8),
                    ft.Text(
                        f"Gmail Label: {newsletter.gmail_label_name}",
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=8),
                    auto_fetch_switch,
                    ft.Container(height=8),
                    interval_field,
                ],
                tight=True,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.app.page.pop_dialog(dialog)),
                ft.ElevatedButton("Save", on_click=lambda e: self.app.page.run_task(save_changes, e)),
            ],
        )

        self.app.page.show_dialog(dialog)

    def _confirm_delete(self, newsletter) -> None:
        """Show confirmation dialog for deletion."""

        async def delete(e: ft.ControlEvent) -> None:
            try:
                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)
                    await service.delete_newsletter(newsletter.id)

                self.app.page.pop_dialog(dialog)
                self.app.show_snackbar(f"Newsletter '{newsletter.name}' deleted")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Delete Newsletter"),
            content=ft.Text(
                f"Are you sure you want to delete '{newsletter.name}'?\n"
                "All emails will also be deleted."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.app.page.pop_dialog(dialog)),
                ft.ElevatedButton(
                    "Delete",
                    color=ft.Colors.ERROR,
                    on_click=lambda e: self.app.page.run_task(delete, e),
                ),
            ],
        )

        self.app.page.show_dialog(dialog)
