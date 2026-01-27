"""Newsletters management page with sophisticated styling."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService
from src.ui.components import AddNewsletterDialog, ConfirmDialog, EditNewsletterDialog, Sidebar
from src.ui.components.gradient_dot import create_gradient_dot
from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors

if TYPE_CHECKING:
    from src.app import NewsletterApp


class NewsletterListItem(ft.Container):
    """List item for newsletter management."""

    def __init__(
        self,
        newsletter,
        on_edit=None,
        on_delete=None,
        colors=None,
    ):
        self.newsletter = newsletter
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._colors = colors or Colors.Light

        # Format auto-fetch text
        if newsletter.auto_fetch_enabled:
            interval = newsletter.fetch_interval_minutes
            if interval >= 1440:
                days = interval // 1440
                auto_fetch_text = f"Every {days} day{'s' if days > 1 else ''}"
            elif interval >= 60:
                hours = interval // 60
                auto_fetch_text = f"Every {hours} hour{'s' if hours > 1 else ''}"
            else:
                auto_fetch_text = f"Every {interval} minutes"
        else:
            auto_fetch_text = "Manual only"

        c = self._colors  # Shorthand

        super().__init__(
            content=ft.Row(
                [
                    # Color dot (with gradient support)
                    create_gradient_dot(
                        newsletter.color or c.ACCENT,
                        newsletter.color_secondary,
                        size=10,
                    ),
                    ft.Container(width=Spacing.SM),
                    # Info
                    ft.Column(
                        [
                            ft.Text(
                                newsletter.name,
                                size=Typography.BODY_SIZE,
                                weight=ft.FontWeight.W_500,
                                color=c.TEXT_PRIMARY,
                            ),
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.LABEL_OUTLINED,
                                        size=12,
                                        color=c.TEXT_TERTIARY,
                                    ),
                                    ft.Container(width=Spacing.XXS),
                                    ft.Text(
                                        newsletter.gmail_label_name,
                                        size=Typography.CAPTION_SIZE,
                                        color=c.TEXT_TERTIARY,
                                    ),
                                    ft.Container(width=Spacing.SM),
                                    ft.Icon(
                                        ft.Icons.SCHEDULE,
                                        size=12,
                                        color=c.TEXT_TERTIARY,
                                    ),
                                    ft.Container(width=Spacing.XXS),
                                    ft.Text(
                                        auto_fetch_text,
                                        size=Typography.CAPTION_SIZE,
                                        color=c.TEXT_TERTIARY,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=Spacing.XXS,
                        expand=True,
                    ),
                    # Actions
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=c.TEXT_TERTIARY,
                        icon_size=18,
                        tooltip="Edit",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda _: self._on_edit(newsletter) if self._on_edit else None,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINED,
                        icon_color=c.ERROR,
                        icon_size=18,
                        tooltip="Delete",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda _: self._on_delete(newsletter) if self._on_delete else None,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=Spacing.MD,
            border_radius=BorderRadius.MD,
            border=ft.border.all(1, c.BORDER_DEFAULT),
            bgcolor=c.BG_PRIMARY,
            on_hover=self._on_hover,
        )

    def _on_hover(self, e: ft.HoverEvent) -> None:
        c = self._colors
        self.border = ft.border.all(
            1,
            c.BORDER_STRONG if e.data == "true" else c.BORDER_DEFAULT,
        )
        self.update()


class NewslettersPage(ft.View):
    """Page for managing newsletters with sidebar."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/newsletters", padding=0, spacing=0)
        self.app = app
        self.newsletters = []

        # Get theme-aware colors
        self.colors = get_colors(self.app.page)

        self.newsletters_list = ft.ListView(
            expand=True,
            spacing=Spacing.SM,
            padding=0,
        )

        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=self.colors.ACCENT,
        )

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.FOLDER_OUTLINED,
                        size=48,
                        color=self.colors.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        "No newsletters yet",
                        size=Typography.H4_SIZE,
                        weight=ft.FontWeight.W_500,
                        color=self.colors.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.XS),
                    ft.Text(
                        "Add a newsletter to get started",
                        size=Typography.BODY_SIZE,
                        color=self.colors.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.LG),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=18, color="#FFFFFF"),
                                ft.Container(width=Spacing.XS),
                                ft.Text("Add Newsletter"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        bgcolor=self.colors.ACCENT,
                        color="#FFFFFF",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda e: self.app.page.run_task(self._show_add_dialog, e),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.Alignment.CENTER,
            visible=False,
        )

        self.sidebar = Sidebar(
            current_route="/newsletters",
            newsletters=[],
            on_navigate=self._handle_navigate,
            page=self.app.page,
        )

        self.controls = [self._build_content()]

        # Load newsletters
        self.app.page.run_task(self._load_newsletters)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        c = self.colors  # Shorthand for readability
        return ft.Row(
            [
                # Sidebar
                self.sidebar,
                # Main content
                ft.Container(
                    content=ft.Column(
                        [
                            # Header
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK,
                                            icon_color=c.TEXT_SECONDARY,
                                            icon_size=20,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda _: self.app.navigate("/home"),
                                        ),
                                        ft.Container(width=Spacing.XS),
                                        ft.Text(
                                            "Manage Newsletters",
                                            size=Typography.H1_SIZE,
                                            weight=ft.FontWeight.W_600,
                                            color=c.TEXT_PRIMARY,
                                        ),
                                        ft.Container(expand=True),
                                        self.loading,
                                        ft.Container(width=Spacing.SM),
                                        ft.ElevatedButton(
                                            content=ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.ADD, size=16, color="#FFFFFF"),
                                                    ft.Container(width=Spacing.XXS),
                                                    ft.Text("Add"),
                                                ],
                                            ),
                                            bgcolor=c.ACCENT,
                                            color="#FFFFFF",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                                padding=ft.padding.symmetric(
                                                    horizontal=Spacing.MD, vertical=Spacing.XS
                                                ),
                                            ),
                                            on_click=lambda e: self.app.page.run_task(
                                                self._show_add_dialog, e
                                            ),
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.LG),
                            ),
                            # Content
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        self.newsletters_list,
                                        self.empty_state,
                                    ],
                                    expand=True,
                                ),
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                    padding=Spacing.LG,
                    expand=True,
                    bgcolor=c.BG_SECONDARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    async def _load_newsletters(self) -> None:
        """Load newsletters from database."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                service = NewsletterService(session=session)
                self.newsletters = await service.get_all_newsletters()

            # Update sidebar
            self.sidebar.update_newsletters(self.newsletters)

            # Update list
            self.newsletters_list.controls.clear()

            if self.newsletters:
                self.empty_state.visible = False
                for newsletter in self.newsletters:
                    item = NewsletterListItem(
                        newsletter=newsletter,
                        on_edit=self._show_edit_dialog,
                        on_delete=self._confirm_delete,
                        colors=self.colors,
                    )
                    self.newsletters_list.controls.append(item)
            else:
                self.empty_state.visible = True

        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    async def _show_add_dialog(self, e) -> None:
        """Show dialog to add a newsletter."""
        try:
            # Get labels from Gmail
            if not self.app.gmail_service:
                self.app.show_snackbar("Not authenticated", error=True)
                return

            labels = await self.app.gmail_service.get_labels_async(user_labels_only=True)
        except Exception as ex:
            self.app.show_snackbar(f"Error loading labels: {ex}", error=True)
            return

        async def save_newsletter(e) -> None:
            try:
                values = dialog.get_values()
                name = (values["name"] or "").strip()
                label_id = values["label_id"]

                if not name:
                    self.app.show_snackbar("Name is required", error=True)
                    return
                if not label_id:
                    self.app.show_snackbar("Label is required", error=True)
                    return

                # Find label name
                label_name = next((l.name for l in labels if l.id == label_id), label_id)

                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)

                    # Check if label already used
                    if await service.label_exists(label_id):
                        self.app.show_snackbar(
                            "A newsletter with this label already exists",
                            error=True,
                        )
                        return

                    newsletter = await service.create_newsletter(
                        name=name,
                        gmail_label_id=label_id,
                        gmail_label_name=label_name,
                        auto_fetch=values["auto_fetch"],
                        fetch_interval=values["interval"],
                        color=values.get("color"),
                        color_secondary=values.get("color_secondary"),
                    )

                # Queue initial email fetch
                if self.app.fetch_queue_service:
                    await self.app.fetch_queue_service.queue_fetch(
                        newsletter.id, FetchPriority.HIGH
                    )

                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar(f"Newsletter '{name}' created")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            dialog.open = False
            self.app.page.update()

        dialog = AddNewsletterDialog(
            labels=labels,
            on_save=lambda e: self.app.page.run_task(save_newsletter, e),
            on_cancel=close_dialog,
            page=self.app.page,
        )

        self.app.page.show_dialog(dialog)

    def _show_edit_dialog(self, newsletter) -> None:
        """Show dialog to edit a newsletter."""

        async def save_changes(e) -> None:
            try:
                values = dialog.get_values()
                name = (values["name"] or "").strip()

                if not name:
                    self.app.show_snackbar("Name is required", error=True)
                    return

                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)
                    await service.update_newsletter(
                        newsletter_id=newsletter.id,
                        name=name,
                        auto_fetch=values["auto_fetch"],
                        fetch_interval=values["interval"],
                        color=values.get("color"),
                        color_secondary=values.get("color_secondary"),
                    )

                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar("Newsletter updated")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            dialog.open = False
            self.app.page.update()

        dialog = EditNewsletterDialog(
            newsletter=newsletter,
            on_save=lambda e: self.app.page.run_task(save_changes, e),
            on_cancel=close_dialog,
            page=self.app.page,
        )

        self.app.page.show_dialog(dialog)

    def _confirm_delete(self, newsletter) -> None:
        """Show confirmation dialog for deletion."""

        async def delete(e) -> None:
            try:
                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)
                    await service.delete_newsletter(newsletter.id)

                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar(f"Newsletter '{newsletter.name}' deleted")
                await self._load_newsletters()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            dialog.open = False
            self.app.page.update()

        dialog = ConfirmDialog(
            title="Delete Newsletter",
            message=f"Are you sure you want to delete '{newsletter.name}'?\nAll emails will also be deleted.",
            confirm_text="Delete",
            cancel_text="Cancel",
            is_destructive=True,
            on_confirm=lambda e: self.app.page.run_task(delete, e),
            on_cancel=close_dialog,
            page=self.app.page,
        )

        self.app.page.show_dialog(dialog)
