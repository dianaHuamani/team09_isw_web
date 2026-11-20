import os
import warnings
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-development-key-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    @staticmethod
    def database_uri():
        database_url = os.getenv("DATABASE_URL", "").strip()
        if database_url:
            if database_url.startswith("mysql://"):
                database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
            return database_url

        # If RDS variables are supplied, compose the MySQL URL without storing
        # credentials in source. Otherwise use a local SQLite database.
        host = os.getenv("DB_HOST")
        if host:
            user = quote_plus(os.getenv("DB_USER", ""))
            password = quote_plus(os.getenv("DB_PASSWORD", ""))
            name = quote_plus(os.getenv("DB_NAME", "farmacia_inkafarma"))
            port = os.getenv("DB_PORT", "3306")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

        warnings.warn(
            "DATABASE_URL no está configurada; la aplicación usará SQLite local, no RDS.",
            RuntimeWarning,
            stacklevel=2,
        )
        instance_dir = BASE_DIR / "instance"
        instance_dir.mkdir(exist_ok=True)
        return f"sqlite:///{instance_dir / 'farmacia.db'}"

    SQLALCHEMY_DATABASE_URI = database_uri.__func__()
