#!/usr/bin/env python3
"""
Google Cloud Setup Script for Mr Newsletter.

This script automates the Google Cloud Console setup process by:
1. Checking/installing gcloud CLI
2. Creating or selecting a GCP project
3. Enabling the Gmail API
4. Guiding through OAuth consent screen setup (manual step)
5. Guiding through OAuth credentials creation (manual step)
6. Saving credentials to .env file
"""

import secrets
import subprocess
import sys
import webbrowser
from pathlib import Path


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_step(step: int, text: str) -> None:
    """Print a step indicator."""
    print(f"{Colors.CYAN}{Colors.BOLD}[Step {step}]{Colors.ENDC} {text}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}! {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}→ {text}{Colors.ENDC}")


def run_command(
    command: list[str], capture_output: bool = True, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print_error(f"Command failed: {' '.join(command)}")
            if e.stderr:
                print(e.stderr)
        raise


def check_gcloud_installed() -> bool:
    """Check if gcloud CLI is installed."""
    try:
        result = run_command(["gcloud", "--version"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_gcloud_authenticated() -> bool:
    """Check if gcloud is authenticated."""
    result = run_command(["gcloud", "auth", "list", "--format=value(account)"], check=False)
    return bool(result.stdout.strip())


def get_active_account() -> str | None:
    """Get the active gcloud account."""
    result = run_command(
        ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
        check=False,
    )
    return result.stdout.strip() or None


def list_projects() -> list[dict]:
    """List available GCP projects."""
    result = run_command(
        ["gcloud", "projects", "list", "--format=json"],
        check=False,
    )
    if result.returncode != 0:
        return []
    import json

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def create_project(project_id: str, project_name: str) -> bool:
    """Create a new GCP project."""
    try:
        run_command(
            ["gcloud", "projects", "create", project_id, f"--name={project_name}"],
        )
        return True
    except subprocess.CalledProcessError:
        return False


def set_project(project_id: str) -> bool:
    """Set the active GCP project."""
    try:
        run_command(["gcloud", "config", "set", "project", project_id])
        return True
    except subprocess.CalledProcessError:
        return False


def enable_gmail_api(project_id: str) -> bool:
    """Enable the Gmail API for the project."""
    try:
        run_command(
            ["gcloud", "services", "enable", "gmail.googleapis.com", f"--project={project_id}"]
        )
        return True
    except subprocess.CalledProcessError:
        return False


def generate_encryption_key() -> str:
    """Generate a secure encryption key."""
    return secrets.token_urlsafe(32)


def get_env_file_path() -> Path:
    """Get the path to the .env file."""
    return Path(__file__).parent.parent / ".env"


def read_env_file() -> dict[str, str]:
    """Read existing .env file if it exists."""
    env_path = get_env_file_path()
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    env_vars[key.strip()] = value.strip()
    return env_vars


def write_env_file(env_vars: dict[str, str]) -> None:
    """Write environment variables to .env file."""
    env_path = get_env_file_path()
    with open(env_path, "w") as f:
        f.write("# Mr Newsletter Environment Configuration\n")
        f.write("# Generated by setup_gcloud.py\n\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{question} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def wait_for_enter(message: str = "Press Enter to continue...") -> None:
    """Wait for user to press Enter."""
    input(f"\n{Colors.YELLOW}{message}{Colors.ENDC}")


def main() -> int:
    """Main setup flow."""
    print_header("Mr Newsletter - Google Cloud Setup")

    print("This script will help you set up Google Cloud credentials for Mr Newsletter.")
    print("It will automate what can be automated and guide you through manual steps.\n")

    # Step 1: Check gcloud CLI
    print_step(1, "Checking gcloud CLI installation...")

    if not check_gcloud_installed():
        print_error("gcloud CLI is not installed.")
        print_info("Please install the Google Cloud SDK from:")
        print(f"  {Colors.CYAN}https://cloud.google.com/sdk/docs/install{Colors.ENDC}")
        print_info("After installation, run this script again.")
        return 1

    print_success("gcloud CLI is installed")

    # Step 2: Check authentication
    print_step(2, "Checking gcloud authentication...")

    if not check_gcloud_authenticated():
        print_warning("Not authenticated with gcloud")
        print_info("Opening browser for authentication...")
        try:
            run_command(["gcloud", "auth", "login"], capture_output=False)
        except subprocess.CalledProcessError:
            print_error("Authentication failed")
            return 1

    active_account = get_active_account()
    if active_account:
        print_success(f"Authenticated as: {active_account}")
    else:
        print_error("Could not determine active account")
        return 1

    # Step 3: Select or create project
    print_step(3, "Setting up GCP project...")

    projects = list_projects()

    if projects:
        print_info(f"Found {len(projects)} existing project(s):")
        for i, project in enumerate(projects[:10], 1):  # Show max 10
            project_id = project.get("projectId", "Unknown")
            project_name = project.get("name", "No name")
            print(f"  {i}. {project_id} ({project_name})")

        if len(projects) > 10:
            print(f"  ... and {len(projects) - 10} more")

        print(f"  {len(projects[:10]) + 1}. Create a new project")

        while True:
            choice = input("\nSelect a project number or enter project ID: ").strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(projects[:10]):
                    project_id = projects[idx]["projectId"]
                    break
                elif idx == len(projects[:10]):
                    # Create new project
                    project_id = None
                    break
            elif choice:
                # Treat as project ID
                project_id = choice
                break

            print_warning("Invalid selection, please try again")
    else:
        print_info("No existing projects found. Creating a new one.")
        project_id = None

    if project_id is None:
        # Create new project
        print_info("Creating a new project...")
        default_id = f"mr-newsletter-{secrets.token_hex(4)}"

        project_id = input(f"Enter project ID [{default_id}]: ").strip() or default_id
        project_name = input("Enter project name [Mr Newsletter]: ").strip() or "Mr Newsletter"

        if create_project(project_id, project_name):
            print_success(f"Created project: {project_id}")
        else:
            print_error("Failed to create project")
            print_info("This might be due to:")
            print("  - Project ID already exists")
            print("  - Billing not enabled")
            print("  - Quota exceeded")
            return 1

    # Set active project
    if set_project(project_id):
        print_success(f"Active project set to: {project_id}")
    else:
        print_error("Failed to set active project")
        return 1

    # Step 4: Enable Gmail API
    print_step(4, "Enabling Gmail API...")

    if enable_gmail_api(project_id):
        print_success("Gmail API enabled")
    else:
        print_error("Failed to enable Gmail API")
        print_info("You may need to enable billing for your project first:")
        print(f"  https://console.cloud.google.com/billing?project={project_id}")
        return 1

    # Step 5: OAuth Consent Screen (Manual)
    print_step(5, "Configuring OAuth Consent Screen (Manual Step)")

    consent_url = f"https://console.cloud.google.com/apis/credentials/consent?project={project_id}"

    print(f"""
{Colors.YELLOW}This step requires manual configuration in the browser.{Colors.ENDC}

{Colors.BOLD}Instructions:{Colors.ENDC}
1. Select "External" user type and click "Create"
2. Fill in the required fields:
   - App name: {Colors.CYAN}Mr Newsletter{Colors.ENDC}
   - User support email: {Colors.CYAN}Your email{Colors.ENDC}
   - Developer contact: {Colors.CYAN}Your email{Colors.ENDC}
3. Click "Save and Continue"
4. On "Scopes" page, click "Add or Remove Scopes"
5. Add these scopes:
   - {Colors.CYAN}https://www.googleapis.com/auth/gmail.readonly{Colors.ENDC}
   - {Colors.CYAN}https://www.googleapis.com/auth/gmail.labels{Colors.ENDC}
6. Click "Save and Continue"
7. On "Test users" page, click "Add Users"
8. Add your Gmail address
9. Click "Save and Continue"
""")

    if prompt_yes_no("Open browser to configure OAuth consent screen?"):
        webbrowser.open(consent_url)
        wait_for_enter("Press Enter after completing the OAuth consent screen setup...")
    else:
        print_info(f"You can configure it later at: {consent_url}")

    # Step 6: Create OAuth Credentials (Manual)
    print_step(6, "Creating OAuth Client Credentials (Manual Step)")

    credentials_url = f"https://console.cloud.google.com/apis/credentials?project={project_id}"

    print(f"""
{Colors.YELLOW}This step requires manual configuration in the browser.{Colors.ENDC}

{Colors.BOLD}Instructions:{Colors.ENDC}
1. Click "Create Credentials" button at the top
2. Select "OAuth client ID"
3. Application type: {Colors.CYAN}Desktop app{Colors.ENDC}
4. Name: {Colors.CYAN}Mr Newsletter Desktop{Colors.ENDC}
5. Click "Create"
6. {Colors.BOLD}Copy the Client ID and Client Secret shown{Colors.ENDC}
""")

    if prompt_yes_no("Open browser to create OAuth credentials?"):
        webbrowser.open(credentials_url)
        wait_for_enter("Press Enter after creating the OAuth credentials...")
    else:
        print_info(f"You can create credentials later at: {credentials_url}")

    # Step 7: Collect credentials
    print_step(7, "Saving credentials to .env file")

    env_vars = read_env_file()

    print(f"\n{Colors.BOLD}Enter your OAuth credentials:{Colors.ENDC}")
    print_info("(Paste each value and press Enter)")

    client_id = input("\nClient ID: ").strip()
    if not client_id:
        print_warning("No Client ID provided. You can add it to .env manually later.")
    else:
        env_vars["GOOGLE_CLIENT_ID"] = client_id

    client_secret = input("Client Secret: ").strip()
    if not client_secret:
        print_warning("No Client Secret provided. You can add it to .env manually later.")
    else:
        env_vars["GOOGLE_CLIENT_SECRET"] = client_secret

    # Generate encryption key if not exists
    if "ENCRYPTION_KEY" not in env_vars or not env_vars["ENCRYPTION_KEY"]:
        env_vars["ENCRYPTION_KEY"] = generate_encryption_key()
        print_success("Generated new encryption key")

    # Write .env file
    write_env_file(env_vars)
    print_success(f"Saved credentials to {get_env_file_path()}")

    # Step 8: Verify and finish
    print_header("Setup Complete!")

    if client_id and client_secret:
        print_success("All required credentials are configured.")
        print(f"""
{Colors.BOLD}Next steps:{Colors.ENDC}
1. Run the application:
   {Colors.CYAN}make run{Colors.ENDC}

2. Sign in with Google when prompted

3. Select the Gmail labels you want to track
""")
    else:
        print_warning("Some credentials are missing.")
        print(f"""
{Colors.BOLD}To complete setup:{Colors.ENDC}
1. Create OAuth credentials at:
   {Colors.CYAN}{credentials_url}{Colors.ENDC}

2. Add to your .env file:
   {Colors.CYAN}GOOGLE_CLIENT_ID=your-client-id{Colors.ENDC}
   {Colors.CYAN}GOOGLE_CLIENT_SECRET=your-client-secret{Colors.ENDC}

3. Run the application:
   {Colors.CYAN}make run{Colors.ENDC}
""")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
