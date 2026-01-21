# Prompts

## Fix macOS .app Bundle Not Opening

**Date:** 2026-01-20

**Issue:** The built `.app` bundle doesn't open when double-clicked or using `open` command, but running the binary directly from command line works fine.

**Root Cause:** PyInstaller's `--onefile` mode (which `flet pack` defaults to) creates a single executable wrapped in a `.app` bundle. This hybrid structure is rejected by macOS Gatekeeper/Launch Services.

**Solution:** Changed from `flet pack` to using PyInstaller directly with `--onedir` mode, which creates a proper directory structure within the `.app` bundle that macOS recognizes as a legitimate application.

**Implementation:** Updated `Makefile` build target to use:
```makefile
build:
	uv run pyinstaller src/main.py \
		--name "Mr Newsletter" \
		--onedir \
		--windowed \
		--add-data "src/config:src/config" \
		--add-data "src/ui:src/ui" \
		--hidden-import flet \
		--hidden-import sqlalchemy \
		--hidden-import asyncpg \
		--hidden-import google.auth \
		--hidden-import apscheduler \
		--hidden-import aiosqlite \
		--collect-all flet \
		--noconfirm \
		--clean
```

## Fix macOS .app Bundle Crash on Double-Click (OAuth Validation)

**Date:** 2026-01-20

**Issue:** App icon appears in Dock briefly then exits immediately when double-clicked. Command line works fine with env vars set.

**Root Cause:** Pydantic Settings validation fails because `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are **required fields with no defaults**. When launched from Finder, shell environment variables aren't available.

**Solution:** Made OAuth credentials optional with empty string defaults in `src/config/settings.py`. The app already has graceful handling for missing OAuth config via `is_app_configured()` check that navigates to a config error page.

**Implementation:**
```python
# BEFORE (crashes on startup)
google_client_id: str = Field(
    description="Google OAuth Client ID from Google Cloud Console",
)

# AFTER (allows startup, shows config error page)
google_client_id: str = Field(
    default="",
    description="Google OAuth Client ID from Google Cloud Console",
)
```

**Key Learning:** macOS `.app` bundles launched from Finder don't inherit shell environment variables. Apps should start successfully and show helpful error pages rather than crashing silently at settings validation.

## Bundle Encrypted App Credentials in .app

**Date:** 2026-01-20

**Issue:** App shows "Configuration Required" error when launched from Finder because OAuth credentials aren't available (environment variables not inherited in macOS `.app` bundles).

**Solution:** Store app credentials (CLIENT_ID/SECRET) in an encrypted file bundled inside the `.app`. The file has a non-obvious name (`.appdata`) for slight obfuscation.

**Implementation:**

1. **Created `scripts/generate_app_config.py`** - Reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from `.env`, encrypts them using Fernet (same encryption as user tokens), and writes to `src/config/.appdata`.

2. **Created `src/config/app_credentials.py`** - Provides `get_app_credentials()` and `is_app_configured()` functions that:
   - Desktop mode: Try bundled encrypted file first, fallback to env vars
   - Web mode: Always use environment variables via Pydantic Settings

3. **Updated `src/services/auth_service.py`** - Now delegates to the new `app_credentials` module for credential loading.

4. **Updated `Makefile`** - Added config generation step before PyInstaller:
   ```makefile
   build:
   	@echo "Generating encrypted app config..."
   	uv run python scripts/generate_app_config.py
   	@echo "Building application with PyInstaller..."
   	uv run pyinstaller ...
   ```

5. **Added `src/config/.appdata` to `.gitignore`** - Credentials never committed to repo.

**Flow:**
- Build time: `generate_app_config.py` reads `.env` → encrypts → writes `.appdata`
- PyInstaller: Bundles `src/config/.appdata` inside the `.app`
- Runtime: App loads credentials from bundled `.appdata` file (desktop) or env vars (web)

**Security Notes:**
- File encrypted with Fernet (same as user tokens)
- Encryption key derived from `ENCRYPTION_KEY` setting
- Non-obvious filename `.appdata` (looks like generic app data)
- File is gitignored (credentials never in repo)

## Fix Desktop App Bundled Config Decryption Error

**Date:** 2026-01-20

**Issue:** Bundled desktop app fails to decrypt `.appdata` with `cryptography.fernet.InvalidToken` error.

**Root Cause:** Key mismatch between build time and runtime:
- **Build**: `generate_app_config.py` uses hardcoded key `"dev-encryption-key-change-in-production"`
- **Runtime**: `decrypt_value()` from `encryption.py` uses `settings.encryption_key` which loads from `.env`
- If `.env` has a different `ENCRYPTION_KEY`, decryption fails

**Solution:** Modified `app_credentials.py` to use a local decryption function with the same hardcoded key used during build, bypassing the settings-based encryption used for user tokens.

**Implementation:**
```python
# src/config/app_credentials.py

# Added constant matching generate_app_config.py
BUNDLED_APP_ENCRYPTION_KEY = "dev-encryption-key-change-in-production"

# Added local decryption function
def _decrypt_bundled_config(ciphertext: str) -> str:
    """Decrypt bundled config using the fixed bundled app key."""
    key_bytes = hashlib.sha256(BUNDLED_APP_ENCRYPTION_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    fernet = Fernet(fernet_key)
    return fernet.decrypt(ciphertext.encode()).decode()

# Replaced decrypt_value() call with _decrypt_bundled_config()
```

**Separation of Concerns:**
1. **Bundled app credentials (.appdata)**: Uses hardcoded key (obfuscation only, consistent across builds)
2. **User tokens (database)**: Uses configurable `ENCRYPTION_KEY` from settings (actual encryption)

**Impact:**
- Web app: Not affected (never calls `_load_from_bundled_file()`)
- Desktop app: Fixed - bundled config decryption now uses correct key

## Fix Desktop App Reload Loop After User Credentials Load Failure

**Date:** 2026-01-20

**Issue:** After fixing bundled config decryption, the app enters a reload loop showing:
```
src.services.auth_service - ERROR - Failed to load user credentials:
```
with an empty error message (no details) and repeated "App session started" logs.

**Root Cause:** User tokens in database were encrypted with a different `ENCRYPTION_KEY` than currently configured:
1. User previously logged in and saved tokens encrypted with one key (from `.env`)
2. Now loading with different/default encryption key → `InvalidToken` exception
3. Exception's string representation is empty, making debugging impossible
4. Auth service returns `None` for credentials → navigates to login → reload cycle continues

The error handler at `auth_service.py:237` was missing `exc_info=True`, hiding the actual exception type.

**Solution:** Two-part fix:
1. **Better logging**: Added `exc_info=True` and exception type to error message
2. **Graceful cleanup**: When credentials can't be decrypted, delete them from database so user can re-authenticate cleanly

**Implementation:**
```python
# src/services/auth_service.py - _load_user_credentials()

# BEFORE
except Exception as e:
    logger.error(f"Failed to load user credentials: {e}")
    return None

# AFTER
except Exception as e:
    logger.error(
        f"Failed to load user credentials ({type(e).__name__}): {e}",
        exc_info=True
    )
    # If decryption fails, the stored credentials are unusable
    # (likely encrypted with a different key). Clear them so user can re-auth.
    if user_cred:
        try:
            await self.session.delete(user_cred)
            await self.session.commit()
            logger.warning(
                "Cleared unusable credentials - user will need to re-authenticate"
            )
        except Exception as cleanup_error:
            logger.error(f"Failed to clear unusable credentials: {cleanup_error}")
    return None
```

**Impact:**
- Web app: Not affected (encryption key consistent via environment variables)
- Desktop app: Fixed - corrupted credentials auto-cleaned, user sees login screen once (not repeatedly)

---

## Fix Desktop App Force Quit on Second Launch

Implement the following plan:

# Fix Desktop App Force Quit on Second Launch

## Problem
The bundled .app works correctly on first launch but fails on subsequent launches - app icon shows in Dock but enters force quit state.

## Solution
1. Register page.on_close handler in src/app.py
2. Add atexit fallback in src/main.py

