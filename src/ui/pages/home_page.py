"""Home page - main dashboard."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class HomePage(ft.View):
    """Main dashboard showing newsletter overview."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/home")
        self.app = app

        self.newsletters_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=350,
            spacing=16,
            run_spacing=16,
        )

        self.loading = ft.ProgressRing(visible=False)
        self.empty_state = ft.Column(
            [
                ft.Icon(
                    ft.icons.INBOX_OUTLINED,
                    size=64,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(height=16),
                ft.Text(
                    "No newsletters yet",
                    size=20,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    "Add a newsletter to get started",
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(height=16),
                ft.ElevatedButton(
                    "Add Newsletter",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self.app.navigate("/newsletters"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        self.appbar = ft.AppBar(
            title=ft.Text("Newsletter Manager"),
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Refresh all",
                    on_click=self._on_refresh_all,
                ),
                ft.IconButton(
                    icon=ft.icons.FOLDER_OUTLINED,
                    tooltip="Manage newsletters",
                    on_click=lambda _: self.app.navigate("/newsletters"),
                ),
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    tooltip="Settings",
                    on_click=lambda _: self.app.navigate("/settings"),
                ),
            ],
        )

        self.controls = [self._build_content()]

        # Load newsletters
        self.app.page.run_task(self._load_newsletters)

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Stack(
                [
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text(
                                            "Your Newsletters",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        self.loading,
                                    ],
                                ),
                                padding=ft.padding.only(bottom=16),
                            ),
                            self.newsletters_grid,
                            self.empty_state,
                        ],
                        expand=True,
                    ),
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
                service = NewsletterService(
                    session=session,
                    gmail_service=self.app.gmail_service,
                )
                newsletters = await service.get_all_newsletters()

            self.newsletters_grid.controls.clear()

            if newsletters:
                self.empty_state.visible = False
                for newsletter in newsletters:
                    card = self._create_newsletter_card(newsletter)
                    self.newsletters_grid.controls.append(card)
            else:
                self.empty_state.visible = True

        except Exception as ex:
            self.app.show_snackbar(f"Error loading newsletters: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_newsletter_card(self, newsletter) -> ft.Control:
        """Create a card for a newsletter."""
        color = newsletter.color or "#6750A4"

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.icons.EMAIL,
                                        color=ft.colors.WHITE,
                                    ),
                                    bgcolor=color,
                                    border_radius=8,
                                    padding=8,
                                ),
                                ft.Container(width=12),
                                ft.Column(
                                    [
                                        ft.Text(
                                            newsletter.name,
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            newsletter.gmail_label_name,
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                        ),
                        ft.Container(height=16),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            str(newsletter.unread_count),
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                            color=color
                                            if newsletter.unread_count > 0
                                            else None,
                                        ),
                                        ft.Text(
                                            "Unread",
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Container(width=24),
                                ft.Column(
                                    [
                                        ft.Text(
                                            str(newsletter.total_count),
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Total",
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                        ),
                        ft.Container(height=16),
                        ft.Row(
                            [
                                ft.TextButton(
                                    "View Emails",
                                    on_click=lambda _, nid=newsletter.id: self.app.navigate(
                                        f"/newsletter/{nid}"
                                    ),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.REFRESH,
                                    tooltip="Fetch now",
                                    on_click=lambda _, nid=newsletter.id: self.app.page.run_task(
                                        self._fetch_newsletter, nid
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                ),
                padding=16,
            ),
        )

    async def _on_refresh_all(self, e: ft.ControlEvent) -> None:
        """Refresh all newsletters."""
        if not self.app.fetch_queue_service:
            return

        async with self.app.get_session() as session:
            service = NewsletterService(session=session)
            newsletters = await service.get_all_newsletters()
            ids = [n.id for n in newsletters]

        queued = await self.app.fetch_queue_service.queue_all_newsletters(
            ids, FetchPriority.HIGH
        )

        self.app.show_snackbar(f"Queued {queued} newsletters for refresh")

    async def _fetch_newsletter(self, newsletter_id: int) -> None:
        """Fetch a single newsletter."""
        if not self.app.fetch_queue_service:
            return

        await self.app.fetch_queue_service.queue_fetch(newsletter_id, FetchPriority.HIGH)
        self.app.show_snackbar("Newsletter queued for refresh")
