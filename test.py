from app.github import extract_repo_info

resultado = extract_repo_info("https://github.com/torvalds/linux")

for arquivo in resultado["files"]:
    print(f"\n--- {arquivo['path']} ---")
    print(arquivo["content"][:200])