from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import predict, explain, reports, analysis
from app.core.config import settings
from app.core.database import engine, Base
import os

# Create the database tables on startup (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="5-Layer Architecture for PCOS Detection (AI + XAI + DB)"
)

# CORS Configuration
origins = ["*"] # Allow all for now, restrict for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Templates (HTML)
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explainability"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
