from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path
from database import engine, Base
from routers import auth, questions, exams, answers, results, users, dashboard, categories, settings, logs, notifications

Base.metadata.create_all(bind=engine)

app = FastAPI(title=" \u4f01\u4e1a\u8003\u6838\u7cfb\u7edf")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# API routes (registered before SPA fallback)
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(answers.router)
app.include_router(results.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(categories.router)
app.include_router(settings.router)
app.include_router(logs.router)
app.include_router(notifications.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "app": " \u4f01\u4e1a\u8003\u6838\u7cfb\u7edf"}

# SPA \u9759\u6001\u6587\u4ef6\u6258\u7ba1\uff08\u6784\u5efa\u540e\u7528 npm run build \u751f\u6210 dist\uff09
dist_path = Path(__file__).parent.parent / "dist"
if dist_path.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")
    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    def serve_spa(full_path: str):
        # Handle uploads - serve static files
        if full_path.startswith("uploads/"):
            uploads_dir = Path(__file__).parent / "public" / "uploads"
            filename = full_path[len("uploads/"):]
            f = uploads_dir / filename
            if f.exists() and f.is_file():
                return FileResponse(str(f))
            return {"status": "not_found"}
        # API routes - skip
        if full_path.startswith("api/"):
            return {"status": "not_found"}
        # SPA
        idx = dist_path / "index.html"
        if not idx.exists():
            return {"status": "not_found"}
        return FileResponse(str(idx))


