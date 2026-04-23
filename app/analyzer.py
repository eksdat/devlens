from groq import Groq
import os
import json
from dotenv import load_dotenv
from app.metrics import run_metrics

load_dotenv()


def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_repo(repo_data: dict) -> dict:
    client = get_client()
    metrics = run_metrics(repo_data)

    files_text = ""
    for file in repo_data["files"]:
        files_text += f"\n\n--- {file['path']} ---\n{file['content']}"

    security_summary = "nenhum problema encontrado"
    if metrics["security"]["total_issues"] > 0:
        issues = [i["type"] for i in metrics["security"]["issues"]]
        security_summary = f"{metrics['security']['total_issues']} problema(s): {', '.join(issues)}"

    deps_summary = metrics["dependencies"]["found"] if metrics["dependencies"]["found"] else "nenhum arquivo de dependencia encontrado"

    prompt = f"""Voce e um engenheiro de software senior fazendo code review de um repositorio GitHub.

Repositorio: {repo_data['owner']}/{repo_data['repo']}

=== METRICAS REAIS DO CODIGO ===
Complexidade ciclomatica media: {metrics['complexity']['average']} (risco: {metrics['complexity']['risk']})
Total de linhas de codigo: {metrics['raw']['total_lines_of_code']}
Ratio de comentarios: {metrics['raw']['comment_ratio']}%
Indice de manutenibilidade: {metrics['maintainability']['index']}/100 (grau {metrics['maintainability']['grade']})
Tem testes: {metrics['tests']['has_tests']} ({metrics['tests']['test_ratio']}% dos arquivos sao testes)
Tem README: {metrics['documentation']['has_readme']}
Arquivos de dependencia: {deps_summary}
Seguranca: {security_summary} (severidade: {metrics['security']['severity']})

=== CODIGO DO REPOSITORIO ===
{files_text}

Com base nas metricas reais acima e no codigo, analise este repositorio.
Responda APENAS em JSON valido, sem texto fora do JSON:
{{
  "proposito": "descricao clara do que o projeto faz",
  "qualidade": "avaliacao detalhada baseada nas metricas reais",
  "pontos_cegos": ["ponto especifico baseado nas metricas", "ponto 2", "ponto 3"],
  "nota": 7,
  "sugestoes": ["sugestao concreta e especifica", "sugestao 2", "sugestao 3"],
  "resumo_executivo": "analise honesta baseada em dados reais"
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
    analysis["architecture"] = generate_architecture(repo_data, client)
    return analysis


def generate_architecture(repo_data: dict, client) -> dict:
    files_text = ""
    for file in repo_data["files"]:
        files_text += f"\n\n--- {file['path']} ---\n{file['content']}"

    prompt = f"""Voce e um arquiteto de software analisando o repositorio {repo_data['owner']}/{repo_data['repo']}.

=== ARQUIVOS DO PROJETO ===
{files_text}

Analise a arquitetura deste projeto e responda APENAS em JSON valido, sem texto fora do JSON:
{{
  "visao_geral": "descricao de como o projeto esta organizado em 2-3 frases",
  "modulos": [
    {{
      "arquivo": "nome do arquivo",
      "responsabilidade": "o que esse modulo faz",
      "depende_de": ["lista de outros arquivos que ele importa ou usa"]
    }}
  ],
  "fluxo_principal": "descreva em passos como uma requisicao flui pelo sistema do inicio ao fim",
  "como_contribuir": "instrucoes praticas para um dev novo comecar a contribuir"
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

    try:
        return json.loads(clean)
    except:
        return {
            "visao_geral": "Nao foi possivel gerar a arquitetura.",
            "modulos": [],
            "fluxo_principal": "",
            "como_contribuir": ""
        }