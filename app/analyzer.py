from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_client() -> Groq:
    """Retorna um cliente Groq autenticado."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_repo(repo_data: dict) -> dict:
    """Analisa um repositório GitHub usando IA e retorna um relatório estruturado."""
    client = get_client()

    files_text = ""
    for file in repo_data["files"]:
        files_text += f"\n\n--- {file['path']} ---\n{file['content']}"

    prompt = f"""Você é um engenheiro de software sênior fazendo code review de um repositório GitHub.

Repositório: {repo_data['owner']}/{repo_data['repo']}

Arquivos encontrados:
{files_text}

Analise este repositório e responda APENAS em JSON válido, sem texto fora do JSON, neste formato exato:
{{
  "proposito": "descrição clara do que o projeto faz",
  "qualidade": "avaliação da qualidade do código",
  "pontos_cegos": ["ponto 1", "ponto 2", "ponto 3"],
  "nota": 7,
  "sugestoes": ["sugestão 1", "sugestão 2", "sugestão 3"],
  "resumo_executivo": "vale a pena contribuir ou usar este projeto?"
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

    return json.loads(clean)