# FEC Campaign Finance MCP Server
# Autor: Reinaldo Chaves (reichaves@gmail.com)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/reichaves/fec-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange)](https://github.com/jlowin/fastmcp)
[![OpenFEC](https://img.shields.io/badge/API-OpenFEC-red)](https://api.open.fec.gov/developers/)

Servidor MCP que conecta a[OpenFEC API](https://api.open.fec.gov/developers/) a assistentes de IA, permitindo investigar o financiamento de campanhas eleitorais federais nos EUA através de conversas naturais.

Projetado para jornalistas de dados, pesquisadores e cidadãos que precisam explorar dados complexos da Comissão Federal de Eleições (FEC) sem conhecer a API diretamente.

---

## Índice

- [O que é o MCP?](#o-que-é-o-mcp)
- [O que este projeto faz?](#o-que-este-projeto-faz)
- [Arquitetura](#arquitetura)
- [Ferramentas disponíveis](#ferramentas-disponíveis)
- [Instalação](#instalação)
-[Configuração no Claude Desktop](#configuração-no-claude-desktop)
- [Configuração no Claude Code e Plataformas CLI](#configuração-no-claude-code-e-plataformas-cli)
-[Exemplos de uso](#exemplos-de-uso)
- [Desenvolvimento e testes](#desenvolvimento-e-testes)
- [Segurança](#segurança)

---

## O que é o MCP?

**MCP (Model Context Protocol)** é um protocolo aberto criado pela Anthropic que define como assistentes de IA se comunicam com sistemas externos — bancos de dados, APIs, arquivos, serviços — de forma padronizada e segura.

Pense no MCP como um "USB" para IA: assim como o USB define um padrão que permite conectar qualquer periférico a qualquer computador, o MCP define um padrão que permite conectar qualquer ferramenta externa a qualquer assistente de IA compatível.

### Os três tipos de capacidade MCP

| Tipo | O que é | Exemplo neste projeto |
|------|---------|----------------------|
| **Tools** | Funções que o AI pode chamar para buscar ou manipular dados | `search_candidates()`, `get_top_donors()` |
| **Resources** | Dados estáticos ou contextuais sempre disponíveis | Tabelas de códigos FEC, IDs notáveis |
| **Prompts** | Templates de workflow que guiam investigações complexas | `investigate_candidate()`, `follow_the_money()` |

---

## O que este projeto faz?

Este projeto expõe a [OpenFEC API](https://api.open.fec.gov/developers/) — base de dados pública da Comissão Federal de Eleições dos EUA — como um servidor MCP. O resultado: você pode investigar financiamento político apenas conversando com o Claude.

### Capacidades principais

- **Busca de candidatos**: Encontre qualquer candidato federal por nome, estado, partido ou cargo
- **Análise financeira**: Totais arrecadados, gastos, dívidas, saldo em caixa (Cash on Hand)
- **Rastreio de doadores**: Identifique os maiores financiadores de uma campanha e seus empregadores
- **Geoanálise**: Veja de quais estados vem o dinheiro de cada candidato
- **Super PACs e gastos independentes**: Monitore grupos externos que gastam para apoiar ou atacar candidatos
- **Relatórios oficiais**: Acesse os filings enviados à FEC por campanhas e comitês
- **Investigação guiada**: Workflows prontos para investigações jornalísticas

### 🔍 Nota Metodológica (OSINT e Arquitetura de Dados)

A API da FEC separa os "Totais do Candidato" (o endpoint primário do comitê oficial) do dinheiro abrigado em Comitês de Ação Política (PACs). Por exemplo, a campanha presidencial de Donald Trump em 2024 apresenta valores residuais em seu endpoint de candidato porque o volume massivo da arrecadação fluiu através de seus *Leadership PACs* (ex: "NEVER SURRENDER, INC.").

O `fec_mcp` foi desenhado estritamente para o princípio de **"Zero Alucinação"**. Ele expõe os dados exatamente como a burocracia governamental os classifica, sem deduções. Na investigação OSINT, cabe ao agente AI ou ao jornalista usar `search_candidates` para listar todos os **Comitês Principais Autorizados e PACs** anexados a um político, e consultar suas finanças individualmente antes de declarar a arrecadação real de uma campanha.

---

## Arquitetura

### Visão geral

```text
fec-mcp-server/
├── README.md                    # Documentação principal em inglês
├── README.pt-br.md              # Documentação principal em português
├── .env.example                 # Exemplo de variáveis de ambiente (chaves de API, idioma)
├── pyproject.toml               # Configuração do projeto e dependências modernas do Python
├── requirements.txt             # Lista de dependências para instalação simples via pip
├── start_server.py              # Entry point: adiciona src/ ao path e inicia o servidor MCP
├── src/fec_mcp/
│   ├── main.py                  # Importa todos os módulos para registrar no FastMCP
│   ├── server.py                # Cria a instância central `mcp = FastMCP(...)`
│   ├── context.py               # Singleton `fec`: instância compartilhada do FECClient
│   ├── client.py                # FECClient ativo: requisições HTTP, retry/backoff, timeouts
│   ├── i18n.py                  # Sistema de internacionalização (carrega textos de /locales)
│   ├── logging_config.py        # Configuração de logging e níveis de verbosidade
│   ├── models.py                # Modelos de dados Pydantic para validação das respostas da API
│   ├── tools/                   # Ferramentas MCP (@mcp.tool)
│   │   ├── candidates.py        # search_candidates, get_candidate_finances
│   │   ├── contributions.py     # search_contributions, get_top_donors, get_contributions_by_state
│   │   ├── expenses.py          # get_campaign_expenditures, get_independent_expenditures, etc
│   │   ├── filings.py           # get_campaign_filings para relatórios financeiros
│   │   ├── search.py            # search_pacs para buscar comitês de ação política
│   │   └── meta.py              # fec_help, suggest_investigation
│   ├── resources/               # Recursos MCP (@mcp.resource)
│   │   └── reference.py         # Códigos FEC, IDs notáveis, glossário, info da API
│   ├── prompts/                 # Prompts MCP (@mcp.prompt)
│   │   └── investigation.py     # investigate_candidate, follow_the_money, compare_candidates
│   ├── data/                    # JSON estáticos usados pelas ferramentas
│   │   ├── glossary.json        # Termos do glossário da FEC
│   │   ├── help.json            # Documentação e exemplos por tópico para a ferramenta fec_help
│   │   └── investigations.json  # Sugestões de pautas jornalísticas
│   └── locales/                 # Arquivos de tradução
│       ├── en.json              # Traduções em inglês
│       └── pt.json              # Traduções em português
└── tests/
    └── test_server.py           # Testes automatizados do cliente e endpoints usando pytest e respx
```

---

## Ferramentas disponíveis

### Tools (funções chamáveis pelo AI)

- `search_candidates`: Busca candidatos federais na base FEC.
- `get_candidate_finances`: Obtém totais financeiros de um candidato.
- `search_contributions`: Busca doações individuais (Schedule A da FEC).
- `get_top_donors`: Lista os maiores doadores de um comitê.
- `get_contributions_by_state`: Agrega doações por estado.
- `get_campaign_expenditures`: Lista os gastos de uma campanha (Schedule B da FEC).
- `get_independent_expenditures`: Busca gastos independentes de Super PACs.
- `get_candidate_filings` / `get_committee_filings`: Lista relatórios financeiros enviados à FEC.
- `search_pacs`: Busca PACs e Super PACs por nome.
- `fec_help`: Documentação interna das ferramentas com exemplos de uso.
- `suggest_investigation`: Sugestões de pautas jornalísticas baseadas em padrões de dados FEC.

### Resources (dados de referência sempre disponíveis)

| URI | Conteúdo |
|-----|----------|
| `fec://reference/codes` | Códigos de partidos, cargos, tipos de comitê, tipos de filing, limites de doação |
| `fec://reference/notable_ids` | IDs de candidatos presidenciais, comitês nacionais, Super PACs relevantes |
| `fec://reference/api_info` | Cobertura dos dados, limites de taxa, dicas de uso |

### Prompts (workflows de investigação)

- `investigate_candidate(candidate_name)`: Workflow passo a passo para investigação financeira completa.
- `follow_the_money(company_name)`: Rastreia a influência política de uma empresa.
- `compare_candidates(candidate1, candidate2)`: Comparação lado a lado de dois candidatos.

---

## Instalação

### Pré-requisitos

- **Python 3.10+**
- **Chave de API da FEC**: gratuita em [api.data.gov/signup](https://api.data.gov/signup/)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/fec-mcp-server.git
cd fec-mcp-server

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o arquivo .env
echo "FEC_API_KEY=sua_chave_aqui" > .env
```

---

## Configuração no Claude Desktop

1. Localize o arquivo de configuração:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Adicione o servidor à configuração:
```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/caminho/absoluto/para/.venv/bin/python",
      "args":["/caminho/absoluto/para/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```
3. Reinicie o Claude Desktop.

---

## Configuração no Claude Code e Plataformas CLI

O protocolo MCP é altamente compatível com agentes de IA baseados em terminal. Veja como configurar em ambientes CLI.

### 1. Claude Code (CLI da Anthropic)

O [Claude Code](https://claude.ai/code) é a ferramenta oficial de terminal da Anthropic. Você pode configurar o servidor MCP da FEC globalmente ou por projeto.

**Método A: Usando o comando CLI**
Execute o comando abaixo no seu terminal (substitua os caminhos pelos caminhos absolutos da sua máquina):
```bash
claude mcp add fec-finance -- /caminho/absoluto/para/.venv/bin/python /caminho/absoluto/para/fec-mcp-server/start_server.py
```
*Nota: Você precisará garantir que a variável `FEC_API_KEY` esteja exportada no seu ambiente de terminal (`export FEC_API_KEY="sua_chave"`) antes de rodar o Claude Code.*

**Método B: Editando o arquivo de configurações (Recomendado para Chaves de API)**
Para garantir que a chave da API seja sempre carregada, edite o arquivo de configuração global em `~/.claude/settings.json` (ou `.claude/settings.json` na raiz do seu projeto):

```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/caminho/absoluto/para/.venv/bin/python",
      "args":["/caminho/absoluto/para/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```
Após salvar, reinicie sua sessão do `claude`. Você pode verificar se está funcionando digitando `/mcp list` dentro do Claude Code.

### 2. Google Antigravity / Gemini CLI

O Antigravity do Google (Gemini CLI Agent) suporta instâncias MCP via stdio. 
Mapeie o servidor no diretório de configuração global do usuário (ex: `%APPDATA%\.gemini\antigravity\mcp.json` no Windows ou `~/.config/gemini/mcp.json` no Linux/macOS):

```json
{
  "mcpServers": {
    "fec-mcp": {
      "command": "/caminho/absoluto/para/.venv/bin/python",
      "args":["/caminho/absoluto/para/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```

### 3. IDEs (Cursor, Windsurf, Continue.dev)

- **Cursor IDE**: Edite `~/.cursor/mcp.json`. A estrutura JSON é idêntica à do Claude Desktop.
- **Continue.dev**: Edite `.continue/config.json` no seu workspace ou configurações globais.
- **Windsurf**: Verifique a documentação oficial do Codeium para o caminho do arquivo de configuração MCP, usando a mesma estrutura JSON.

---

## Exemplos de uso

### Investigar um candidato

> *"Investigue o financiamento da campanha de Kamala Harris em 2024"*

O Claude executará automaticamente:
1. `search_candidates(name="Kamala Harris", election_year=2024)`
2. `get_candidate_finances(candidate_id="P00009423")`
3. `get_top_donors(committee_id="C00703975")`

### Rastrear dinheiro corporativo

> *"Quais candidatos recebem mais dinheiro de funcionários da Goldman Sachs?"*

```
search_contributions(contributor_employer="Goldman Sachs", election_cycle=2024)
```

### Comparar candidatos

> *"Compare o financiamento de Trump e Biden para 2024"*

O prompt `compare_candidates` gera uma tabela completa com todas as métricas lado a lado.

---

## Desenvolvimento e testes

```bash
# Rodar todos os testes
pytest tests/

# Verificar lint
ruff check src/
```

## Limitações conhecidas

- **Dados federais apenas**: eleições estaduais e municipais não estão na FEC
- **Dark money**: doações para 501(c)(4) não são divulgadas à FEC
- **Latência**: endpoints de doações individuais (`schedule_a`) podem ser lentos
- **Rate limit**: 1.000 requisições/hora com chave de API gratuita

---

## Segurança

Este servidor roda **localmente** na sua máquina e faz requisições **somente de leitura** à API pública da FEC. Não manipula credenciais de usuário nem dados pessoais (PII).

Práticas adotadas:
- Guarde sua chave de API no `.env` apenas — nunca faça commit (`.env` está no `.gitignore`)
- A chave de API é mascarada automaticamente em todo output de log (`SecretFilter`)
- Logs rodam com rotação a 5 MB e estão excluídos do controle de versão
- Nomes de arquivos lidos do disco são restritos a uma lista de permissões explícita

Para o modelo de ameaças completo, declaração de compatibilidade com Skill Vetter/Socket/Snyk, instruções de auditoria de dependências e como reportar vulnerabilidades, veja [SECURITY.md](SECURITY.md).

---

## Recursos externos

- [OpenFEC API — Documentação](https://api.open.fec.gov/developers/)
- [FEC — Site oficial](https://www.fec.gov/)
-[OpenSecrets](https://www.opensecrets.org/)
- [FastMCP — Documentação](https://github.com/jlowin/fastmcp)
- [MCP — Especificação do protocolo](https://modelcontextprotocol.io/)
