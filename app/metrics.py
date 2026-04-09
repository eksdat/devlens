from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
import re


def analyze_complexity(content: str) -> dict:
    """Calcula complexidade ciclomática do código Python."""
    try:
        blocks = cc_visit(content)
        if not blocks:
            return {"average": 0, "max": 0, "functions": []}

        complexities = [b.complexity for b in blocks]
        functions = [
            {
                "name": b.name,
                "complexity": b.complexity,
                "risk": classify_risk(b.complexity)
            }
            for b in blocks
        ]

        return {
            "average": round(sum(complexities) / len(complexities), 2),
            "max": max(complexities),
            "functions": functions
        }
    except:
        return {"average": 0, "max": 0, "functions": []}


def analyze_raw(content: str) -> dict:
    """Analisa linhas de código, comentários e espaços em branco."""
    try:
        raw = analyze(content)
        total = raw.loc if raw.loc > 0 else 1
        return {
            "lines_of_code": raw.loc,
            "comments": raw.comments,
            "blank_lines": raw.blank,
            "comment_ratio": round((raw.comments / total) * 100, 1)
        }
    except:
        return {"lines_of_code": 0, "comments": 0, "blank_lines": 0, "comment_ratio": 0}


def analyze_maintainability(content: str) -> dict:
    """Calcula índice de manutenibilidade (0-100)."""
    try:
        mi = mi_visit(content, multi=True)
        return {
            "index": round(mi, 1),
            "grade": classify_maintainability(mi)
        }
    except:
        return {"index": 0, "grade": "N/A"}


def detect_test_files(files: list) -> dict:
    """Detecta presença e proporção de arquivos de teste."""
    total = len(files)
    test_files = [
        f for f in files
        if "test" in f["path"].lower() or "spec" in f["path"].lower()
    ]

    return {
        "total_files": total,
        "test_files": len(test_files),
        "has_tests": len(test_files) > 0,
        "test_ratio": round((len(test_files) / total) * 100, 1) if total > 0 else 0,
        "test_paths": [f["path"] for f in test_files]
    }


def detect_documentation(files: list) -> dict:
    """Detecta presença de documentação."""
    doc_names = ["readme.md", "readme.rst", "readme.txt", "contributing.md", "changelog.md"]
    
    doc_files = [
        f for f in files
        if f["path"].split("/")[-1].lower() in doc_names
    ]

    has_readme = any(
        f["path"].split("/")[-1].lower().startswith("readme")
        for f in files
    )

    return {
        "has_readme": has_readme,
        "doc_files": [f["path"] for f in doc_files],
        "doc_count": len(doc_files)
    }


def detect_dependencies(files: list, contents: dict) -> dict:
    """Detecta arquivos de dependência e verifica presença."""
    dep_names = ["requirements.txt", "package.json", "pipfile", "pyproject.toml", "setup.py"]
    
    found = [
        f["path"].split("/")[-1]
        for f in files
        if f["path"].split("/")[-1].lower() in dep_names
    ]

    return {
        "has_dependency_file": len(found) > 0,
        "found": found
    }


def classify_risk(complexity: int) -> str:
    if complexity <= 5:
        return "low"
    elif complexity <= 10:
        return "medium"
    elif complexity <= 20:
        return "high"
    return "very_high"


def classify_maintainability(mi: float) -> str:
    if mi >= 80:
        return "A"
    elif mi >= 60:
        return "B"
    elif mi >= 40:
        return "C"
    return "D"


def run_metrics(repo_data: dict) -> dict:
    """Executa todas as métricas no repositório."""
    files = repo_data["files"]
    python_files = [f for f in files if f["path"].endswith(".py")]

    all_complexity = []
    all_raw = []
    all_mi = []

    for file in python_files:
        content = file["content"]
        all_complexity.append(analyze_complexity(content))
        all_raw.append(analyze_raw(content))
        all_mi.append(analyze_maintainability(content))

    # Agrega complexidade
    complexities = [c["average"] for c in all_complexity if c["average"] > 0]
    avg_complexity = round(sum(complexities) / len(complexities), 2) if complexities else 0

    # Agrega raw
    total_loc = sum(r["lines_of_code"] for r in all_raw)
    total_comments = sum(r["comments"] for r in all_raw)
    comment_ratio = round((total_comments / total_loc) * 100, 1) if total_loc > 0 else 0

    # Agrega manutenibilidade
    mi_scores = [m["index"] for m in all_mi if m["index"] > 0]
    avg_mi = round(sum(mi_scores) / len(mi_scores), 1) if mi_scores else 0

    contents = {f["path"]: f["content"] for f in files}

    return {
        "complexity": {
            "average": avg_complexity,
            "risk": classify_risk(int(avg_complexity))
        },
        "raw": {
            "total_lines_of_code": total_loc,
            "total_comments": total_comments,
            "comment_ratio": comment_ratio
        },
        "maintainability": {
            "index": avg_mi,
            "grade": classify_maintainability(avg_mi)
        },
        "tests": detect_test_files(files),
        "documentation": detect_documentation(files),
        "dependencies": detect_dependencies(files, contents)
    }