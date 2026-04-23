from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.github import extract_repo_info
from app.analyzer import analyze_repo
from pathlib import Path
import asyncio

app = FastAPI(title="DevLens", description="Analisa repositórios GitHub com IA", version="1.0.0")

class RepoRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
def root():
    html = Path("templates/index.html").read_text()
    return HTMLResponse(content=html)

@app.post("/analyze")
async def analyze(request: RepoRequest):
    try:
        loop = asyncio.get_event_loop()
        repo_data = await loop.run_in_executor(None, extract_repo_info, request.url)
        analysis = await loop.run_in_executor(None, analyze_repo, repo_data)
        return {"repo": f"{repo_data['owner']}/{repo_data['repo']}", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))