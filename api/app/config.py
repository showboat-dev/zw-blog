from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    admin_username: str = "admin"
    admin_password: str = "change-me"
    session_secret: str = "dev-session-secret-change-me-32b"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_oauth_callback_url: str = "http://localhost:8000/api/auth/github/callback"
    public_web_origin: str = "http://localhost:5173"
    database_url: str = "sqlite+aiosqlite:///./data/blog.db"
    upload_dir: str = "./data/uploads"
    cookie_secure: bool = False


settings = Settings()
