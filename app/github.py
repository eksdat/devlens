import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_repo_files(owner: str, repo: str, path: str = "") -> list:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar repositório: {response.status_code}")
    
    items = response.json()
    files = []

    for item in items:
        if item["type"] == "file" and item["name"].endswith((".py", ".js", ".ts", ".md", ".json")):
            files.append({
                "name": item["name"],
                "path": item["path"],
                "download_url": item["download_url"]
            })
        elif item["type"] == "dir":
            files.extend(get_repo_files(owner, repo, item["path"]))

    return files


def get_file_content(download_url: str) -> str:
    response = requests.get(download_url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    return ""


def extract_repo_info(github_url: str) -> dict:
    parts = github_url.rstrip("/").split("/")
    owner = parts[-2]
    repo = parts[-1]
    
    files = get_repo_files(owner, repo)
    
    repo_content = []
    for file in files[:10]:  # limite de 10 arquivos por enquanto
        content = get_file_content(file["download_url"])
        repo_content.append({
            "path": file["path"],
            "content": content[:3000]  # limite de caracteres por arquivo
        })
    
    return {
        "owner": owner,
        "repo": repo,
        "files": repo_content
    }