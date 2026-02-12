class MermaidAIError(Exception):
    """Базовое исключение приложения."""


class MermaidValidationError(MermaidAIError):
    """Невалидный Mermaid-код (пустой или синтаксическая ошибка)."""


class MermaidRateLimitError(MermaidAIError):
    """Превышен лимит запросов (например, Kroki 429)."""


class MermaidServiceUnavailableError(MermaidAIError):
    """Сервис недоступен (таймаут, 5xx, сетевая ошибка)."""


class MermaidOutputError(MermaidAIError):
    """Некорректный ответ сервиса (пустое тело, неверный Content-Type)."""


class MermaidIOError(MermaidAIError):
    """Ошибка записи файла на диск."""


class LLMExternalServiceError(RuntimeError):
    """Финальная ошибка после всех retry"""
