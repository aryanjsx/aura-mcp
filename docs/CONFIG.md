# Configuration Reference

AURA loads configuration from three layers (later layers override earlier ones):

1. **Built-in defaults** — hardcoded in `config/loader.py`
2. **YAML config file** — `aura_mcp/config/config.yaml` (or a custom path)
3. **Environment variables** — always take highest priority

## Config File

Default location: `aura_mcp/config/config.yaml`

```yaml
workspace: ~/projects
default_stack: fastapi
log_level: info
llm_mode: openai
github_enabled: true
docker_enabled: true

notion:
  api_key: ""
  database_id: ""

openai:
  api_key: ""
  model: gpt-3.5-turbo

github:
  token: ""
```

## All Options

| Key | Type | Default | Env Override | Description |
|-----|------|---------|-------------|-------------|
| `workspace` | string | `~/projects` | `AURA_WORKSPACE` | Root directory for scaffolded projects |
| `default_stack` | string | `fastapi` | — | Default framework when none is detected |
| `log_level` | string | `info` | `AURA_LOG_LEVEL` | Logging level (debug, info, warning, error) |
| `llm_mode` | string | `openai` | `AURA_LLM_MODE` | LLM provider: `openai` or `local` |
| `github_enabled` | bool | `true` | — | Enable the GitHub plugin |
| `docker_enabled` | bool | `true` | — | Enable the Docker plugin |
| `notion.api_key` | string | `""` | `NOTION_API_KEY` | Notion integration token |
| `notion.database_id` | string | `""` | `NOTION_DATABASE_ID` | Notion database to read tasks from |
| `openai.api_key` | string | `""` | `OPENAI_API_KEY` | OpenAI API key |
| `openai.model` | string | `gpt-3.5-turbo` | `OPENAI_MODEL` | Chat model to use |
| `github.token` | string | `""` | `GITHUB_TOKEN` | GitHub personal access token |

## Generating a Starter Config

```bash
aura init
```

This copies the default config into your current directory as
`aura_config.yaml`.

## Verifying Your Setup

```bash
aura doctor
```

This checks Python version, required environment variables, config file
presence, LLM mode, and discovered plugins.
