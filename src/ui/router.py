"""UI Router for page navigation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app import NewsletterApp


class Router:
    """Router for handling page navigation."""

    def __init__(self, app: "NewsletterApp"):
        """Initialize router.

        Args:
            app: Main application instance.
        """
        self.app = app

    def navigate(self, route: str) -> None:
        """Navigate to a route.

        Args:
            route: Route to navigate to.
        """
        self.app.navigate(route)

    def go_home(self) -> None:
        """Navigate to home page."""
        self.navigate("/home")

    def go_login(self) -> None:
        """Navigate to login page."""
        self.navigate("/login")

    def go_setup(self) -> None:
        """Navigate to setup page."""
        self.navigate("/setup")

    def go_newsletters(self) -> None:
        """Navigate to newsletters management page."""
        self.navigate("/newsletters")

    def go_newsletter(self, newsletter_id: int) -> None:
        """Navigate to newsletter email list.

        Args:
            newsletter_id: Newsletter ID.
        """
        self.navigate(f"/newsletter/{newsletter_id}")

    def go_email(self, email_id: int) -> None:
        """Navigate to email reader.

        Args:
            email_id: Email ID.
        """
        self.navigate(f"/email/{email_id}")

    def go_settings(self) -> None:
        """Navigate to settings page."""
        self.navigate("/settings")

    def go_back(self) -> None:
        """Go back to previous page."""
        self.app.page.views.pop()
        if self.app.page.views:
            top_view = self.app.page.views[-1]
            self.app.page.go(top_view.route)
