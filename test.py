from app.github import extract_repo_info
from app.analyzer import analyze_repo
import json

repo_data = extract_repo_info("https://github.com/eksdat/devlens")
analise = analyze_repo(repo_data)

print(json.dumps(analise, indent=2, ensure_ascii=False))