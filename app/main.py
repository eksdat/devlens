from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.github import extract_repo_info
from app.analyzer import analyze_repo
from pathlib import Path

app = FastAPI(title="DevLens", description="Analisa repositórios GitHub com IA", version="1.0.0")

class RepoRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
def root():
    html = Path("templates/index.html").read_text()
    return HTMLResponse(content=html)

@app.post("/analyze")
def analyze(request: RepoRequest):
    try:
        repo_data = extract_repo_info(request.url)
        analysis = analyze_repo(repo_data)
        return {"repo": f"{repo_data['owner']}/{repo_data['repo']}", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))