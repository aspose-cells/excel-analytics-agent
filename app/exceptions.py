class ExcelAgentError(Exception):
    """Base exception for all Excel AI Agent errors."""


class AnalysisError(ExcelAgentError):
    """Raised when an analysis tool fails to execute."""


class PipelineError(ExcelAgentError):
    """Raised when a pipeline stage fails."""


class PlannerError(ExcelAgentError):
    """Raised when the LLM planner fails."""


class ExcelReadError(ExcelAgentError):
    """Raised when reading an Excel file fails."""


class ExcelWriteError(ExcelAgentError):
    """Raised when writing an Excel file fails."""


class ToolNotFoundError(ExcelAgentError):
    """Raised when a requested tool is not found in the registry."""


class ConfigurationError(ExcelAgentError):
    """Raised when required configuration is missing."""


class StateError(ExcelAgentError):
    """Raised when state persistence fails."""
