import os

class Settings:
    PROJECT_NAME: str = "PCOS Intelligent Diagnostic System"
    PROJECT_VERSION: str = "1.0.0"

    # Database: use Postgres in production (Vercel sets DATABASE_URL)
    _db_url: str = os.getenv("DATABASE_URL", "sqlite:///./pcos_db.db")
    DATABASE_URL: str = (
        _db_url.replace("postgres://", "postgresql://", 1)
        if _db_url.startswith("postgres://")
        else _db_url
    )

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-production")

    # ML model: host the .joblib externally (Vercel Blob/S3) to avoid the 500MB bundle limit
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH",
        "/tmp/pcos_voting_ensemble.joblib" if os.getenv("VERCEL") else "pcos_voting_ensemble.joblib",
    )
    MODEL_URL: str | None = os.getenv("MODEL_URL")

    SHAP_EXPLAINER_PATH: str = os.getenv(
        "SHAP_EXPLAINER_PATH",
        "/tmp/shap_explainer.joblib" if os.getenv("VERCEL") else "shap_explainer.joblib",
    )
    SHAP_EXPLAINER_URL: str | None = os.getenv("SHAP_EXPLAINER_URL")

settings = Settings()
