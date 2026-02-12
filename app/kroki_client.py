import logging

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from app.exceptions import (
    MermaidIOError,
    MermaidOutputError,
    MermaidRateLimitError,
    MermaidServiceUnavailableError,
    MermaidValidationError,
)
from app.logger import setup_logger
from app.settings import settings

logger = setup_logger(__name__, log_level=logging.INFO)


def mermaid_to_png(mermaid_code: str, output_file: str, timeout: int = 10) -> None:
    """
    Отправляет Mermaid-код на API сервиса Kroki, получает PNG и записывает в output_file.
    """
    logger.info("Начинаю рендер Mermaid -> PNG: %s", output_file)

    if not mermaid_code or not mermaid_code.strip():
        logger.warning("Пустой Mermaid код")
        raise MermaidValidationError("Empty Mermaid code")

    try:
        logger.debug("Отправка запроса на Kroki: %s",
                     settings.KROKI_MERMAID_PNG_ENDPOINT)
        response = requests.post(
            url=f"{settings.KROKI_BASE_URL}{settings.KROKI_MERMAID_PNG_ENDPOINT}",
            data=mermaid_code.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=timeout,
        )
        logger.debug("Ответ от Kroki: %d %s", response.status_code, response.reason)

        if response.status_code == 400:
            logger.warning("Неверный синтаксис Mermaid")
            raise MermaidValidationError("Invalid Mermaid syntax")

        if response.status_code == 413:
            logger.warning("Слишком большая диаграмма")
            raise MermaidValidationError("Mermaid diagram is too large")

        if response.status_code == 429:
            logger.warning("Превышен лимит Kroki")
            raise MermaidRateLimitError("Kroki rate limit exceeded")

        if response.status_code >= 500:
            logger.error("Ошибка сервера Kroki: %d", response.status_code)
            raise MermaidServiceUnavailableError(
                f"Kroki server error: {response.status_code}"
            )

        response.raise_for_status()

        if not response.content:
            logger.error("Пустой ответ от Kroki")
            raise MermaidOutputError("Empty response from Kroki")

        content_type = response.headers.get("Content-Type", "")
        if "image/png" not in content_type:
            logger.error("Unexpected content type: %s", content_type)
            raise MermaidOutputError(f"Unexpected content type: {content_type}")

        try:
            with open(output_file, "wb") as f:
                f.write(response.content)
            logger.info("Файл PNG успешно сохранён: %s", output_file)
        except OSError as e:
            logger.exception("Не удалось записать PNG файл")
            raise MermaidIOError("Failed to write PNG file") from e

    except Timeout as e:
        logger.warning("Kroki request timed out")
        raise MermaidServiceUnavailableError("Kroki request timed out") from e

    except ConnectionError as e:
        logger.warning("Не удалось подключиться к Kroki")
        raise MermaidServiceUnavailableError("Connection to Kroki failed") from e

    except HTTPError as e:
        logger.error("HTTP ошибка от Kroki")
        raise MermaidServiceUnavailableError("HTTP error from Kroki") from e

    except RequestException as e:
        logger.error("Неожиданная ошибка запроса к Kroki")
        raise MermaidServiceUnavailableError("Unexpected request error") from e
