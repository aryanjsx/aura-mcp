# 🔒 Security Policy

## Supported Versions

| Version | Supported |
|:--------|:----------|
| 0.1.x   | ✅ Current |

## Reporting a Vulnerability

If you discover a security vulnerability in AURA MCP, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Instead, email the maintainer or open a private security advisory on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within **48 hours**
- A fix or mitigation within **7 days** for critical issues
- Credit in the changelog (unless you prefer to remain anonymous)

## Security Measures in AURA MCP

### Input Validation

- All task text is validated before processing
- LLM output is parsed and validated against a strict schema
- Project names are sanitized: lowercased, special characters stripped, max 64 characters
- Framework must be in an explicit whitelist (`react`, `node`, `fastapi`)

### No Arbitrary Execution

- AURA does **not** execute shell commands from task input
- AURA does **not** run `eval()` or dynamic code execution
- AURA does **not** install packages or run dependency managers
- Only predefined project templates are scaffolded

### API Key Safety

- All secrets are loaded from environment variables via `dotenv`
- `.env` is gitignored — never committed to the repository
- API keys are never logged or included in Notion output

### Filesystem Safety

- Project names are sanitized to prevent path traversal (`../`)
- Output is restricted to the `output/` directory
- Files are only created, never modified or deleted

### LLM Safety

- Single API call per task — no chains or loops that could escalate
- LLM output is never executed as code
- LLM output is always validated before use
- Automatic fallback to deterministic rule-based parsing on any failure

## Dependencies

We recommend regularly auditing dependencies:

```bash
npm audit
```

Report any vulnerable dependency findings via GitHub Issues.
