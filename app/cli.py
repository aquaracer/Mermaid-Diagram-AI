import logging

from app.ai_client import MermaidAIClient
from app.exceptions import (
    LLMExternalServiceError,
    MermaidIOError,
    MermaidRateLimitError,
    MermaidServiceUnavailableError,
    MermaidValidationError,
)
from app.kroki_client import mermaid_to_png
from app.logger import setup_logger
from app.settings import Settings

logger = setup_logger(__name__, log_level=logging.INFO)


def main():
    print("🤖 Mermaid Diagram Bot")
    print("Опишите диаграмму или напишите 'exit' для выхода.\n")

    settings = Settings()
    ai = MermaidAIClient(settings)

    while True:
        try:
            description = input("Вы: ").strip()

            if description.lower() in {"exit", "quit"}:
                print("Бот: До свидания 👋")
                logger.info("Пользователь завершил работу бота")
                break

            if not description:
                print("Бот: Пожалуйста, введите описание диаграммы.")
                continue

            print("Бот: Генерирую Mermaid код...")
            logger.info("Начинаю генерацию Mermaid кода для описания")
            result = ai.generate(description)
            logger.info("Mermaid код сгенерирован успешно")

            output_file = "diagram.png"
            print("Бот: Рендерю PNG через Kroki...")
            logger.info("Рендер PNG в файл: %s", output_file)
            mermaid_to_png(mermaid_code=result, output_file=output_file)

            print(f"Бот: ✅ Файл готов — {output_file}")
            logger.info("Файл PNG успешно создан: %s", output_file)
            print("Бот: Можете ввести новое описание или 'exit' для выхода.\n")

        except LLMExternalServiceError as e:
            print(f"Бот: ❌ Ошибка LLM сервиса: {e}")
            logger.error("Ошибка LLM сервиса: %s", e)
            print("Бот: Попробуйте ещё раз.\n")

        except MermaidValidationError as e:
            print(f"Бот: ❌ Ошибка в диаграмме: {e}")
            logger.warning("Ошибка в диаграмме: %s", e)
            print("Бот: Попробуйте переформулировать описание.\n")

        except MermaidRateLimitError:
            print("Бот: ⏳ Превышен лимит запросов. Попробуйте позже.\n")
            logger.warning("Превышен лимит запросов Kroki")

        except MermaidServiceUnavailableError:
            print("Бот: 🌐 Сервис рендеринга временно недоступен.\n")
            logger.warning("Сервис рендеринга Kroki недоступен")

        except MermaidIOError:
            print("Бот: 💾 Ошибка записи файла.\n")
            logger.error("Ошибка записи файла PNG")


        except Exception as e:
            print(f"Бот: ⚠️ Непредвиденная ошибка: {e}\n")
            logger.exception("Непредвиденная ошибка в main: %s", e)


if __name__ == "__main__":
    main()
