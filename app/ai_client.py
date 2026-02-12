import logging
import time

import openai
from pydantic import ValidationError

from app.exceptions import LLMExternalServiceError
from app.logger import setup_logger
from app.settings import Settings
from app.validators import validate_mermaid_response

logger = setup_logger(__name__, log_level=logging.DEBUG)


class MermaidAIClient:
    def __init__(self, settings: Settings):
        self.client = openai.OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=settings.LLM_REQUEST_TIMEOUT,
        )
        self.settings = settings

    def generate(self, description: str) -> str:
        prompt = f"""Ты — инженер, который генерирует Mermaid диаграммы.

    Требования:
    - Верни ТОЛЬКО Mermaid code
    - Без JSON
    - Без markdown
    - Без комментариев
    - Mermaid должен быть валидным и готовым к рендерингу
    - Никакого дополнительного текста

    Описание:
    {description}
    """

        last_error = None
        logger.info("=== Начало генерации Mermaid диаграммы ===")

        for attempt in range(1, self.settings.LLM_MAX_RETRIES + 1):
            logger.debug("Попытка %d/%d", attempt, self.settings.LLM_MAX_RETRIES)
            try:
                response = self.client.chat.completions.create(
                    model=self.settings.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1,
                )
                logger.debug("Ответ LLM получен: %s", response)

                if not response or not response.choices:
                    raise ValueError("Empty choices in LLM response")

                message = response.choices[0].message
                if not message or not message.content:
                    raise ValueError("Empty message content from LLM")

                content = message.content.strip()
                if not content:
                    raise ValueError("LLM returned empty content")

                validate_mermaid_response(response=content)
                logger.info("✅ Генерация успешна")
                return content


            except (
                    openai.RateLimitError,
                    openai.APITimeoutError,
                    openai.APIConnectionError,
                    openai.APIError,
                    TimeoutError,
            ) as e:
                last_error = e
                sleep_time = min(2 ** attempt, 30)
                logger.warning(
                    "Сетевая ошибка или таймаут: %s. Повтор через %ds", e, sleep_time
                )
                time.sleep(sleep_time)

            except (ValidationError, ValueError, IndexError, KeyError, TypeError) as e:
                last_error = e
                sleep_time = min(2 ** attempt, 30)
                logger.warning(
                    "Ошибка генерации / валидации: %s. Повтор через %ds", e, sleep_time
                )
                time.sleep(sleep_time)

            except (
                    openai.AuthenticationError,
                    openai.PermissionDeniedError,
                    openai.NotFoundError,
            ) as e:
                logger.error("Фатальная ошибка LLM-конфигурации: %s", e)
                raise LLMExternalServiceError(
                    "Fatal LLM configuration error"
                ) from e

        logger.error(
            "❌ LLM генерация не удалась после %d попыток: %s",
            self.settings.LLM_MAX_RETRIES,
            last_error,
        )
        raise LLMExternalServiceError(
            f"LLM generation failed after {self.settings.LLM_MAX_RETRIES} attempts"
        ) from last_error
