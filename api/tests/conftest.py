import os
import sys
from pathlib import Path

os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "secret")
os.environ.setdefault("SESSION_SECRET", "test-session-secret-32-bytes-min")
os.environ.setdefault("PUBLIC_WEB_ORIGIN", "http://testserver")
os.environ.setdefault("GITHUB_CLIENT_ID", "test-id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-secret")
os.environ.setdefault(
    "GITHUB_OAUTH_CALLBACK_URL",
    "http://testserver/api/auth/github/callback",
)

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
