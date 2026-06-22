# Compliance Framework

## Data Handling Policy

This project processes Excel files containing user data. The following policies apply:

### Data Classification
- **Input files**: User-provided Excel spreadsheets
- **Output files**: Analysis results with annotations
- **Temporary data**: Session logs, execution history

### Data Retention
- Session logs: Retained for 30 days, then auto-purged
- Execution history: Stored in `output/sessions/` for audit trail
- Users may request deletion at any time

### Privacy
- No data is sent to third parties except the configured LLM API
- LLM API calls only transmit column names and analysis requests, not raw data values
- API keys are stored in environment variables, never committed

## Governance

### Access Control
- Environment variables control API access
- Docker deployment supports network isolation
- File system permissions protect output data

### Audit Trail
- All executions are logged with timestamps
- Session state is persisted for traceability
- CI/CD pipeline provides build and deployment history

## Standards Alignment

This framework aligns with:
- SOC2 (Security, Availability, Confidentiality)
- GDPR (Data processing transparency, right to deletion)
- ISO 27001 (Information security management principles)
