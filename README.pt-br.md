# FEC Campaign Finance MCP Server
# Autor: Reinaldo Chaves (reichaves@gmail.com)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/reichaves/fec-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange)](https://github.com/jlowin/fastmcp)
[![OpenFEC](https://img.shields.io/badge/API-OpenFEC-red)](https://api.open.fec.gov/developers/)

Servidor MCP que conecta a [OpenFEC API](https://api.open.fec.gov/developers/) a assistentes de IA, permitindo investigar o financiamento de campanhas eleitorais federais nos EUA através de conversas naturais.

Projetado para jornalistas de dados, pesquisadores e cidadãos que precisam explorar dados complexos da Comissão Federal de Eleições (FEC) sem conhecer a API diretamente.

---

## Índice

- [O que é o MCP?](#o-que-é-o-mcp)
- [O que este projeto faz?](#o-que-este-projeto-faz)
- [Arquitetura](#arquitetura)
- [Ferramentas disponíveis](#ferramentas-disponíveis)
- [Instalação](#instalação)
- [Configuração no Claude Desktop](#configuração-no-claude-desktop)
- [Outras plataformas compatíveis](#outras-plataformas-compatíveis)
- [Exemplos de uso](#exemplos-de-uso)
- [Desenvolvimento e testes](#desenvolvimento-e-testes)
- [Segurança](#segurança)

---

## O que é o MCP?

**MCP (Model Context Protocol)** é um protocolo aberto criado pela Anthropic que define como assistentes de IA se comunicam com sistemas externos — bancos de dados, APIs, arquivos, serviços — de forma padronizada e segura.

Pense no MCP como um "USB" para IA: assim como o USB define um padrão que permite conectar qualquer periférico a qualquer computador, o MCP define um padrão que permite conectar qualquer ferramenta externa a qualquer assistente de IA compatível.

### Como o MCP funciona na prática

Sem MCP, um assistente de IA só tem acesso ao que está na conversa. Com MCP, o fluxo funciona assim:

```
Usuário ──→ Claude Desktop ──→ Servidor MCP ──→ OpenFEC API
                                    │                 │
                                    └── retorna dados ─┘
                                    │
                ←── resposta formatada ──┘
```

1. O usuário faz uma pergunta: *"Quanto Trump arrecadou em 2024?"*
2. O Claude identifica que precisa de dados externos e chama uma **Tool** do servidor MCP
3. O servidor MCP recebe a chamada, consulta a FEC API com os parâmetros corretos
4. Os dados retornam ao Claude, que os interpreta e responde em linguagem natural

### Os três tipos de capacidade MCP

| Tipo | O que é | Exemplo neste projeto |
|------|---------|----------------------|
| **Tools** | Funções que o AI pode chamar para buscar ou manipular dados | `search_candidates()`, `get_top_donors()` |
| **Resources** | Dados estáticos ou contextuais sempre disponíveis | Tabelas de códigos FEC, IDs notáveis |
| **Prompts** | Templates de workflow que guiam investigações complexas | `investigate_candidate()`, `follow_the_money()` |

### Protocolo de comunicação

O MCP usa **JSON-RPC 2.0** sobre **stdio** (entrada/saída padrão). O Claude Desktop inicia o processo do servidor e se comunica com ele via stdin/stdout. Não é necessário abrir portas ou configurar redes — o servidor roda localmente como um processo filho.

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

### Dados disponíveis

A FEC cobre **eleições federais** (Presidente, Senado, Câmara) desde 1979. Dados estaduais e municipais **não estão incluídos**. Os dados são atualizados diariamente conforme os filings chegam à FEC.

### 🔍 Nota Metodológica (OSINT e Arquitetura de Dados)

A API da FEC separa os "Totais do Candidato" (o endpoint primário do comitê oficial) do dinheiro abrigado em Comitês de Ação Política (PACs). Por exemplo, a campanha presidencial de Donald Trump em 2024 apresenta valores residuais em seu endpoint de candidato porque o volume massivo da arrecadação fluiu através de seus *Leadership PACs* (ex: "NEVER SURRENDER, INC.").

O `fec_mcp` foi desenhado estritamente para o princípio de **"Zero Alucinação"**. Ele expõe os dados exatamente como a burocracia governamental os classifica, sem deduções. Na investigação OSINT, cabe ao agente AI ou ao jornalista usar `search_candidates` para listar todos os **Comitês Principais Autorizados e PACs** anexados a um político, e consultar suas finanças individualmente antes de declarar a arrecadação real de uma campanha.

### Histórico de Atualizações (Melhorias Recentes)
- **Correção Temporal (Bug Trump 2016):** Substituição do parâmetro depreciado `election_year` pelo parâmetro correto `cycle` em toda a base de código (Endpoints financeiros agora respeitam ciclos estritos).
- **Aviso Anti-Alucinação:** A ferramenta `get_candidate_finances` agora gera um alerta (no campo "tip") caso o ciclo de retorno da OpenFEC difira do ciclo solicitado, evitando erros analíticos.
- **Limpeza de Dívida Técnica:** Remoção total do cliente duplicado `fec_client.py`, unificando a integração via `client.py` com suporte ao retry exponencial e timeouts.

---

## Arquitetura

### Visão geral

```
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

### Padrão de registro FastMCP

O FastMCP usa decorators para registrar capacidades. A instância central `mcp` vive em [src/fec_mcp/server.py](src/fec_mcp/server.py). **Para que uma tool/resource/prompt seja registrada, seu módulo precisa ser importado em [src/fec_mcp/main.py](src/fec_mcp/main.py)**. Adicionar um novo arquivo sem importá-lo em `main.py` faz com que ele seja invisível para o cliente MCP.

```python
# main.py — importações explícitas para registro
import fec_mcp.tools.candidates      # registra: search_candidates, get_candidate_finances
import fec_mcp.tools.contributions   # registra: search_contributions, get_top_donors, ...
import fec_mcp.resources.reference   # registra: fec://reference/codes, fec://reference/notable_ids, ...
import fec_mcp.prompts.investigation  # registra: investigate_candidate, follow_the_money, ...
```

### O cliente HTTP (client.py)

O `FECClient` em [src/fec_mcp/client.py](src/fec_mcp/client.py) gerencia todas as chamadas à API com:

- **Timeouts diferenciados**: endpoints lentos como `schedule_a` (doações individuais) recebem 120s; demais recebem 30s
- **Retry com backoff exponencial**: tenta novamente em erros 429 (rate limit) e 503 (serviço indisponível)
- **Sleep progressivo em timeout**: aguarda antes de retornar erro para evitar cascata de falhas

O singleton `fec` em [src/fec_mcp/context.py](src/fec_mcp/context.py) é o que todas as tools importam.

---

## Ferramentas disponíveis

### Tools (funções chamáveis pelo AI)

#### `search_candidates`
Busca candidatos federais na base FEC.
- Parâmetros: `name`, `state`, `office` (P/S/H), `party` (DEM/REP/LIB/GRE), `election_year`
- Retorna: lista com `candidate_id`, nome, partido, estado, cargo, ciclos eleitorais e comitês principais

#### `get_candidate_finances`
Obtém totais financeiros de um candidato.
- Parâmetros: `candidate_id`, `election_year`
- Retorna: total arrecadado, gasto, saldo em caixa, dívidas, contribuições individuais, de PACs e autofinanciamento

#### `search_contributions`
Busca doações individuais (Schedule A da FEC).
- Parâmetros: `contributor_name`, `contributor_employer`, `contributor_state`, `committee_id`, `min_amount`, `max_amount`, `election_cycle`
- Retorna: lista de doações com doador, empregador, ocupação, valor, data

#### `get_top_donors`
Lista os maiores doadores de um comitê, agregados por doador e por empregador.
- Parâmetros: `committee_id`, `min_amount` (padrão: $1.000), `election_cycle`
- Retorna: top 20 doadores e top 10 empregadores com totais

#### `get_contributions_by_state`
Agrega doações por estado — útil para análise geográfica.
- Parâmetros: `committee_id`, `election_cycle`
- Retorna: lista ordenada por total, com contagem e valor por estado

#### `get_campaign_expenditures`
Lista os gastos de uma campanha (Schedule B da FEC).
- Parâmetros: `committee_id`, `min_amount`, `purpose`, `election_cycle`
- Retorna: gastos com fornecedor, propósito, valor, data

#### `get_independent_expenditures`
Busca gastos independentes de Super PACs a favor ou contra candidatos.
- Parâmetros: `candidate_id`, `support_oppose` (S/O), `election_cycle`
- Retorna: gastos externos com PAC, valor, candidato apoiado/atacado

#### `get_independent_expenditures_summary`
Resumo agregado dos gastos independentes por PAC.

#### `get_candidate_filings` / `get_committee_filings`
Lista relatórios financeiros enviados à FEC.
- Retorna: tipo de filing (F3, F3P, F3X etc.), período coberto, datas

#### `search_pacs`
Busca PACs e Super PACs por nome.

#### `search_committees_by_type`
Lista comitês por tipo (Super PAC, PAC qualificado, partido etc.).

#### `fec_help`
Documentação interna das ferramentas com exemplos de uso.
- Tópicos: `candidates`, `contributions`, `expenditures`, `pacs`, `filings`, `workflows`, `ids`

#### `suggest_investigation`
Sugestões de pautas jornalísticas baseadas em padrões de dados FEC.
- Áreas: `money_in_politics`, `dark_money`, `local`, `corporate`, `foreign`

### Resources (dados de referência sempre disponíveis)

| URI | Conteúdo |
|-----|----------|
| `fec://reference/codes` | Códigos de partidos, cargos, tipos de comitê, tipos de filing, limites de doação 2024 |
| `fec://reference/notable_ids` | IDs de candidatos presidenciais 2024, comitês nacionais, Super PACs relevantes |
| `fec://reference/api_info` | Cobertura dos dados, limites de taxa, dicas de uso |

### Prompts (workflows de investigação)

#### `investigate_candidate(candidate_name)`
Workflow passo a passo para investigação financeira completa de um candidato: busca do ID, finanças gerais, top doadores, análise geográfica, gastos da campanha e gastos independentes de Super PACs.

#### `follow_the_money(company_name)`
Rastreia a influência política de uma empresa: funcionários que doaram, preferência partidária, existência de PAC corporativo, possíveis conflitos de interesse.

#### `compare_candidates(candidate1, candidate2)`
Comparação lado a lado de dois candidatos: totais financeiros, perfil de doadores, geografia do dinheiro e apoio externo de Super PACs. Gera tabela comparativa.

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

# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
pip install -e ".[dev]"   # inclui pytest, ruff, respx

# 4. Crie o arquivo .env
echo "FEC_API_KEY=sua_chave_aqui" > .env

# 5. Teste o servidor diretamente (opcional)
python start_server.py
```

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `FEC_API_KEY` | Sim | Chave da OpenFEC API |
| `FEC_API_BASE_URL` | Não | URL base da API (padrão: `https://api.open.fec.gov/v1`) |

---

## Configuração no Claude Desktop

O Claude Desktop é a forma mais direta de usar este servidor MCP. Ele inicia o servidor automaticamente quando você abre o app e o encerra quando fecha.

### 1. Localize o arquivo de configuração

| Sistema | Caminho |
|---------|---------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. Edite o arquivo de configuração

Abra o arquivo (crie-o se não existir) e adicione o servidor:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/caminho/absoluto/para/.venv/bin/python",
      "args": ["/caminho/absoluto/para/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "C:\\Users\\SeuUsuario\\fec-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\SeuUsuario\\fec-mcp-server\\start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```

> **Dica**: Para descobrir o caminho correto do Python no ambiente virtual, ative o venv e execute `which python` (macOS/Linux) ou `where python` (Windows).

### 3. Reinicie o Claude Desktop

Feche completamente e reabra o Claude Desktop. Se a configuração estiver correta, você verá um ícone de ferramentas (hammer) na interface indicando que os servidores MCP estão ativos.

### 4. Verifique a conexão

Pergunte ao Claude: *"Quais ferramentas você tem disponíveis sobre FEC?"* — ele deve listar as tools deste servidor.

---

## Outras plataformas compatíveis

O MCP é um protocolo aberto. Além do Claude Desktop, este servidor pode ser usado com qualquer cliente que implemente o protocolo MCP:

### Claude Code (CLI)

O [Claude Code](https://claude.ai/code) suporta MCP nativamente. Adicione o servidor ao arquivo de configuração do projeto (`.claude/settings.json`) ou globalmente (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/caminho/para/.venv/bin/python",
      "args": ["/caminho/para/start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```

### Google Antigravity / Gemini CLI

O Google Antigravity (ambiente de AI Agent via Gemini) suporta instâncias do protocolo MCP. Para integrar, o servidor deve ser mapeado na configuração global do usuário no diretório App Data (como `%APPDATA%\.gemini\antigravity\mcp.json` no Windows ou via configurações de ambiente dependendo da instalação). O formato de conexão baseia-se na inicialização via stdio:

```json
{
  "mcpServers": {
    "fec-mcp": {
      "command": "C:\\Caminho\\Para\\fec-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Caminho\\Para\\fec-mcp-server\\start_server.py"],
      "env": {
        "FEC_API_KEY": "SUA_CHAVE_FEC_AQUI"
      }
    }
  }
}
```

### Cursor IDE

O [Cursor](https://cursor.sh/) suporta MCP via configuração em `~/.cursor/mcp.json`. A estrutura é idêntica à do Claude Desktop.

### Windsurf (Codeium)

O [Windsurf](https://codeium.com/windsurf) suporta MCP. Verifique a documentação oficial para o caminho do arquivo de configuração.

### Continue.dev

O [Continue](https://continue.dev/) é uma extensão para VS Code e JetBrains com suporte a MCP via arquivo `.continue/config.json`.

### Aplicações personalizadas via SDK

Se você quer integrar este servidor MCP em uma aplicação própria, use o SDK Python da Anthropic:

```python
import anthropic

client = anthropic.Anthropic()

# Conexão com o servidor MCP local
with client.beta.mcp.sessions.connect(
    server_command=["/caminho/.venv/bin/python", "/caminho/start_server.py"],
    server_env={"FEC_API_KEY": "sua_chave"}
) as session:
    # Liste as tools disponíveis
    tools = session.list_tools()
    print([t.name for t in tools])
```

### Tabela de compatibilidade

| Plataforma | Suporte MCP | Observação |
|-----------|-------------|-----------|
| Claude Desktop | Nativo | Configuração mais simples |
| Claude Code (CLI) | Nativo | Ideal para uso em terminal |
| Google Antigravity | Nativo | Plataforma oficial Gemini CLI Agent |
| Cursor IDE | Nativo | Bom para desenvolvimento |
| Windsurf | Nativo | Verificar versão mínima |
| Continue.dev | Via extensão | VS Code e JetBrains |
| Apps customizados | Via SDK Python/TS | Máxima flexibilidade |
| n8n / Make | Via HTTP (MCP over SSE) | Requer adaptador SSE |

> **Nota sobre transporte**: Este servidor usa **stdio** (padrão para uso local). Para integrações web ou multi-usuário, o MCP também suporta **SSE (Server-Sent Events)** via HTTP — mas isso requer configuração adicional e não é coberto aqui.

---

## Exemplos de uso

### Investigar um candidato

> *"Investigue o financiamento da campanha de Kamala Harris em 2024"*

O Claude executará automaticamente:
1. `search_candidates(name="Kamala Harris", election_year=2024)`
2. `get_candidate_finances(candidate_id="P00009423")`
3. `get_top_donors(committee_id="C00703975")`
4. `get_contributions_by_state(committee_id="C00703975")`
5. `get_independent_expenditures(candidate_id="P00009423")`

### Rastrear dinheiro corporativo

> *"Quais candidatos recebem mais dinheiro de funcionários da Goldman Sachs?"*

```
search_contributions(contributor_employer="Goldman Sachs", election_cycle=2024)
```

### Monitorar Super PACs

> *"Quais Super PACs estão gastando dinheiro contra candidatos democratas?"*

```
get_independent_expenditures_summary(support_oppose="O", party="DEM")
```

### Comparar candidatos

> *"Compare o financiamento de Trump e Biden para 2024"*

O prompt `compare_candidates` gera uma tabela completa com todas as métricas lado a lado.

---

## Desenvolvimento e testes

```bash
# Rodar todos os testes
pytest tests/

# Rodar um teste específico
pytest tests/test_server.py::test_search_candidates

# Excluir testes lentos
pytest tests/ -m "not slow"

# Verificar lint
ruff check src/

# Iniciar servidor para debug manual
python start_server.py
```

### Estrutura dos testes

Os testes usam `respx` para interceptar chamadas HTTP ao `httpx`, simulando respostas da FEC API sem necessidade de internet ou chave real. A fixture `FEC_API_KEY=TEST_KEY` é definida em `conftest.py`.

Como o FastMCP envolve as funções em wrappers, para chamar uma tool diretamente nos testes use:

```python
result = await search_candidates.fn(name="Biden")
```

### Adicionando uma nova tool

1. Crie ou edite um arquivo em `src/fec_mcp/tools/`
2. Decore a função com `@mcp.tool()`
3. Importe o módulo em `src/fec_mcp/main.py`
4. Escreva o teste correspondente em `tests/`

```python
# src/fec_mcp/tools/minha_tool.py
from ..server import mcp
from ..context import fec

@mcp.tool()
async def minha_tool(param: str) -> str:
    """Descrição clara — o Claude usa isso para decidir quando chamar a tool."""
    try:
        result = await fec.algum_endpoint(param)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

```python
# src/fec_mcp/main.py — adicione a importação
import fec_mcp.tools.minha_tool
```

---

## Limitações conhecidas

- **Dados federais apenas**: eleições estaduais e municipais não estão na FEC
- **Dark money**: doações para 501(c)(4) não são divulgadas à FEC — esses grupos aparecem como gastadores mas seus financiadores são ocultos
- **Latência**: endpoints de doações individuais (`schedule_a`) podem ser lentos (timeout configurado em 120s)
- **Rate limit**: 1.000 requisições/hora com chave de API gratuita
- **Defasagem**: dados podem estar 24–48h atrás dos filings mais recentes

---

## Segurança

Este servidor roda **localmente** na sua máquina e faz requisições **somente de leitura** à API pública da FEC. Não manipula credenciais de usuário nem dados pessoais (PII).

Práticas adotadas:
- Guarde sua chave de API no `.env` apenas — nunca faça commit (`.env` está no `.gitignore`)
- A chave de API é mascarada automaticamente em todo output de log (`SecretFilter`)
- Logs rodam com rotação a 5 MB e estão excluídos do controle de versão
- Nomes de arquivos lidos do disco são restritos a uma lista de permissões explícita

Para o modelo de ameaças completo, declaração de compatibilidade com Skill Vetter/Socket/Snyk, instruções de auditoria de dependências e como reportar vulnerabilidades, veja [SECURITY.md](SECURITY.md).

```bash
# Auditar dependências por CVEs conhecidos
pip-audit

# Análise estática de segurança
bandit -r src/

# Rodar testes focados em segurança
pytest tests/test_security.py -v
```

---

## Recursos externos

- [OpenFEC API — Documentação](https://api.open.fec.gov/developers/)
- [FEC — Site oficial](https://www.fec.gov/)
- [OpenSecrets](https://www.opensecrets.org/) — complemento com dados de dark money e contexto histórico
- [FastMCP — Documentação](https://github.com/jlowin/fastmcp)
- [MCP — Especificação do protocolo](https://modelcontextprotocol.io/)
- [Obter chave da API](https://api.data.gov/signup/)
