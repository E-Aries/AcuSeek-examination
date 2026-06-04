from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path
from database import engine, Base
from routers import auth, questions, exams, answers, results

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AXUS 企业考核系统")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(answers.router)
app.include_router(results.router)

# SPA 静态文件托管（构建后用 npm run build 生成 dist）
dist_path = Path(__file__).parent.parent / "dist"
if dist_path.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "" or not (dist_path / "index.html").exists():
            return {"status": "not_found"}
        return FileResponse(str(dist_path / "index.html"))

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "AXUS 企业考核系统"}
