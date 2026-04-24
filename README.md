# DevLens

> Analise qualquer repositório GitHub com inteligência artificial e métricas reais de código.

**Demo:** [devlens-1ayp.onrender.com](https://devlens-1ayp.onrender.com)

---

## O que é o DevLens?

DevLens é uma ferramenta que vai além de um simples wrapper de IA. Ela combina **análise estática real de código** com **inteligência artificial** para entregar um relatório completo de qualquer repositório GitHub público.

Diferente de ferramentas que apenas mandam o código para uma IA e esperam uma resposta, o DevLens primeiro coleta métricas concretas e objetivas, e só então usa a IA para interpretar esses dados — resultando em análises muito mais precisas e úteis.

---

## Funcionalidades

- **Métricas reais de código** — complexidade ciclomática, índice de manutenibilidade, linhas de código e ratio de comentários calculados com a biblioteca `radon`
- **Análise de segurança** — detecção de padrões perigosos como SQL injection, secrets hardcoded, uso de `eval`, shell injection e debug mode ativo
- **Detecção de dependências** — identifica automaticamente `requirements.txt`, `package.json`, `pyproject.toml` e outros
- **Cobertura de testes** — detecta e mede a proporção de arquivos de teste no projeto
- **Análise com IA** — usa LLaMA 3.3 70B via Groq para interpretar as métricas e gerar insights contextualizados
- **Score multicritério** — nota de 0 a 10 baseada em dados reais, não em achismos
- **Interface web moderna** — dashboard dark mode com cards organizados por categoria

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI |
| Análise estática | Radon |
| IA | LLaMA 3.3 70B via Groq API |
| Dados | GitHub REST API |
| Frontend | HTML + CSS + JavaScript puro |
| Deploy | Render |

---

## Como rodar localmente

### Pré-requisitos
- Python 3.10+
- Conta no [GitHub](https://github.com) com token de acesso
- Conta no [Groq](https://console.groq.com) com API key gratuita

### Instalação

```bash
git clone https://github.com/eksdat/devlens
cd devlens
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
GITHUB_TOKEN=seu_token_aqui
GROQ_API_KEY=sua_chave_aqui
```

### Execução

```bash
uvicorn app.main:app --reload
```

Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Como funciona

```
URL do repositório
        ↓
GitHub API → coleta arquivos (.py, .js, .ts, .md, .json)
        ↓
Análise estática → complexidade, manutenibilidade, testes, segurança, dependências
        ↓
LLaMA 3.3 70B → interpreta métricas + código e gera análise contextualizada
        ↓
Dashboard → exibe tudo em cards organizados com score final
```

---

## Estrutura do projeto

```
devlens/
├── app/
│   ├── main.py        # API FastAPI + rotas
│   ├── github.py      # Integração com GitHub API
│   ├── analyzer.py    # Integração com Groq/LLaMA
│   └── metrics.py     # Análise estática com Radon
├── templates/
│   └── index.html     # Interface web
├── requirements.txt
└── .env               # Variáveis de ambiente (não commitado)
```

---

## Métricas analisadas

| Métrica | Ferramenta | O que mede |
|---|---|---|
| Complexidade ciclomática | Radon | Número de caminhos independentes no código |
| Índice de manutenibilidade | Radon | Facilidade de manter e evoluir o código (0-100) |
| Ratio de comentários | Radon | Proporção de comentários vs linhas de código |
| Cobertura de testes | Detecção por padrão | % de arquivos dedicados a testes |
| Vulnerabilidades | Regex + padrões | SQL injection, secrets, eval, shell injection |
| Dependências | Detecção por nome | Presença de arquivo de gerenciamento de deps |
