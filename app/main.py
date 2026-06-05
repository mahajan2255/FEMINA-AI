from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import predict, explain, reports, analysis, auth
from app.core.config import settings
from app.core.database import engine, Base
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="5-Layer Architecture for PCOS Detection (AI + XAI + DB)",
    lifespan=lifespan,
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explainability"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
