class AgentError(Exception):
    pass

class DataValidationError(AgentError):
    pass

class SecurityError(AgentError):
    pass

class LLMGenerationError(AgentError):
    pass

class ConfigurationError(AgentError):
    pass