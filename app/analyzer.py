from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_repo(repo_data: dict) -> dict:
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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    clean = response.text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    return json.loads(clean)