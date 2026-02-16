import os

class Settings:
    PROJECT_NAME: str = "PCOS Intelligent Diagnostic System"
    PROJECT_VERSION: str = "1.0.0"
    
    # PostgreSQL Connection
    DATABASE_URL: str = "postgresql+psycopg2://postgres:Srmid-492913@localhost/pcos_db"

settings = Settings()
