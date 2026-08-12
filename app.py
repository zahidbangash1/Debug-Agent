"""
app.py — FastAPI entry point
Serves HTML templates + mounts API routes from backend.py
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from backend import router as api_router

load_dotenv()

app = FastAPI(title="Debugging Agent", version="1.0.0")

# CORS (for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# API routes
app.include_router(api_router)

# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.get("/")
async def home(request: Request):
    # ✅ FIXED: FastAPI modern TemplateResponse syntax
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

# ─── Run Server ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)