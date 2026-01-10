"""Home page - main dashboard with sidebar navigation."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService
from src.ui.components import NewsletterCard, Sidebar
from src.ui.themes import BorderRadius, Colors, Spacing, Typography

if TYPE_CHECKING:
    from src.app import NewsletterApp


class HomePage(ft.View):
    """Main dashboard showing newsletter overview with sidebar."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/home", padding=0, spacing=0)
        self.app = app
        self.newsletters = []

        self.newsletters_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=350,
            spacing=Spacing.MD,
            run_spacing=Spacing.MD,
            padding=0,
        )

        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=Colors.Light.ACCENT,
        )

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.INBOX_OUTLINED,
                        size=48,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        "No newsletters yet",
                        size=Typography.H4_SIZE,
                        weight=ft.FontWeight.W_500,
                        color=Colors.Light.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.XS),
                    ft.Text(
                        "Add a newsletter to get started",
                        size=Typography.BODY_SIZE,
                        color=Colors.Light.TEXT_TERTIARY,
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
                        bgcolor=Colors.Light.ACCENT,
                        color="#FFFFFF",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda _: self.app.navigate("/newsletters"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.Alignment.CENTER,
            visible=False,
        )

        self.sidebar = Sidebar(
            current_route="/home",
            newsletters=[],
            on_navigate=self._handle_navigate,
        )

        self.controls = [self._build_content()]

        # Load newsletters
        self.app.page.run_task(self._load_newsletters)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        return ft.Row(
            [
                # Sidebar
                self.sidebar,
                # Main content
                ft.Container(
                    content=ft.Column(
                        [
                            # Page header
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text(
                                            "Home",
                                            size=Typography.H1_SIZE,
                                            weight=ft.FontWeight.W_600,
                                            color=Colors.Light.TEXT_PRIMARY,
                                        ),
                                        ft.Container(expand=True),
                                        self.loading,
                                        ft.Container(width=Spacing.SM),
                                        ft.IconButton(
                                            icon=ft.Icons.REFRESH,
                                            icon_color=Colors.Light.TEXT_SECONDARY,
                                            icon_size=20,
                                            tooltip="Refresh all",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda e: self.app.page.run_task(
                                                self._on_refresh_all, e
                                            ),
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.LG),
                            ),
                            # Content area
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        self.newsletters_grid,
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
                    bgcolor=Colors.Light.BG_SECONDARY,
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
                service = NewsletterService(
                    session=session,
                    gmail_service=self.app.gmail_service,
                )
                self.newsletters = await service.get_all_newsletters()

            self.newsletters_grid.controls.clear()

            if self.newsletters:
                self.empty_state.visible = False
                for newsletter in self.newsletters:
                    card = self._create_newsletter_card(newsletter)
                    self.newsletters_grid.controls.append(card)
                # Update sidebar with newsletters
                self.sidebar.update_newsletters(self.newsletters)
            else:
                self.empty_state.visible = True

        except Exception as ex:
            self.app.show_snackbar(f"Error loading newsletters: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_newsletter_card(self, newsletter) -> ft.Control:
        """Create a card for a newsletter."""
        return NewsletterCard(
            name=newsletter.name,
            label=newsletter.gmail_label_name,
            unread_count=newsletter.unread_count,
            total_count=newsletter.total_count,
            color=newsletter.color,
            on_click=lambda _, nid=newsletter.id: self.app.navigate(
                f"/newsletter/{nid}"
            ),
            on_refresh=lambda _, nid=newsletter.id: self.app.page.run_task(
                self._fetch_newsletter, nid
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
