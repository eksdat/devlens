from groq import Groq
import os
import json
from dotenv import load_dotenv
from app.metrics import run_metrics

load_dotenv()

def get_client() -> Groq:
    """Retorna um cliente Groq autenticado."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_repo(repo_data: dict) -> dict:
    """Analisa um repositório GitHub usando métricas reais + IA."""
    client = get_client()

    # Métricas reais primeiro
    metrics = run_metrics(repo_data)

    files_text = ""
    for file in repo_data["files"]:
        files_text += f"\n\n--- {file['path']} ---\n{file['content']}"

    prompt = f"""Você é um engenheiro de software sênior fazendo code review de um repositório GitHub.

Repositório: {repo_data['owner']}/{repo_data['repo']}

=== MÉTRICAS REAIS DO CÓDIGO ===
Complexidade ciclomática média: {metrics['complexity']['average']} (risco: {metrics['complexity']['risk']})
Total de linhas de código: {metrics['raw']['total_lines_of_code']}
Ratio de comentários: {metrics['raw']['comment_ratio']}%
Índice de manutenibilidade: {metrics['maintainability']['index']}/100 (grau {metrics['maintainability']['grade']})
Tem testes: {metrics['tests']['has_tests']} ({metrics['tests']['test_ratio']}% dos arquivos são testes)
Tem README: {metrics['documentation']['has_readme']}
Arquivos de dependência: {metrics['dependencies']['found']}

=== CÓDIGO DO REPOSITÓRIO ===
{files_text}

Com base nas métricas reais acima e no código, analise este repositório.
Responda APENAS em JSON válido, sem texto fora do JSON:
{{
  "proposito": "descrição clara do que o projeto faz",
  "qualidade": "avaliação detalhada baseada nas métricas reais",
  "pontos_cegos": ["ponto específico baseado nas métricas", "ponto 2", "ponto 3"],
  "nota": 7,
  "sugestoes": ["sugestão concreta e específica", "sugestão 2", "sugestão 3"],
  "resumo_executivo": "análise honesta baseada em dados reais"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    clean = response.choices[0].message.content.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    analysis = json.loads(clean)
    analysis["metrics"] = metrics

    return analysis