import re

ALLOWED_STARTS = (
    "graph TD",
    "graph LR",
    "flowchart TD",
    "flowchart LR",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "gantt",
)

FORBIDDEN_PATTERNS = [
    r"```",  # markdown
    r"\{.*\}",  # JSON
    r"\"diagram_",  # остатки старого формата
    r"^\s*$",  # полностью пустой
]


def validate_mermaid_response(response: str) -> tuple[bool, str]:
    """
    Проверяет, что строка является на валидным Mermaid-кодом.

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(response, str):
        return False, "Response is not a string"

    response = response.strip()

    if not response:
        return False, "Response is empty"

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, response, re.MULTILINE | re.DOTALL):
            return False, f"Forbidden pattern detected: {pattern}"

    first_line = response.splitlines()[0].strip()
    if not any(first_line.startswith(start) for start in ALLOWED_STARTS):
        return False, "Invalid Mermaid start line"

    if "->" not in response and "class" not in response and "participant" not in response:
        return False, "No Mermaid structural elements detected"

    suspicious_lines = [
        line for line in response.splitlines()
        if not re.match(r'^[\w\s\-\>\:\|\[\]\(\)\{\}\"\'\.\;\,\<\>\=]+$', line)
    ]
    if suspicious_lines:
        return False, "Suspicious non-Mermaid content detected"

    return True, "Valid Mermaid"
