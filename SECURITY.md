# Security Policy

## Supported Versions

The following versions are currently receiving security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.7.x   | :white_check_mark: |
| < 0.7   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it via email to **security@example.com**.

Do **not** open a public GitHub issue for security vulnerabilities.

We will acknowledge receipt within 48 hours and provide an estimated timeline for a fix. You will be updated as the investigation progresses.

## Disclosure Policy

- Vulnerabilities are patched in a private release before public disclosure.
- Once a fix is released, we will publish a security advisory via GitHub.
- We request a 90-day embargo period from the time a fix is released before any public disclosure.

## Security Best Practices

- **API Keys**: Never commit API keys or secrets to version control. Use environment variables or a `.env` file (see `.env.example`).
- **Input Validation**: Always validate and sanitize data loaded from external CSV/Excel files before processing.
- **Dependencies**: Keep all dependencies up to date. Run `pip-audit` or `npm audit` regularly.
- **Container Security**: When using Docker, avoid running containers as root. Use the `USER` directive in Dockerfiles.
- **Logging**: Do not log sensitive information (tokens, passwords, PII). Use structured logging with appropriate levels.
- **LLM Safety**: When using LLM-based planning, validate generated tool calls against an allow-list to prevent prompt injection.
