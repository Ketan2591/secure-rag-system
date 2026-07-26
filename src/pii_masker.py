import re

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Presidio engines are created once and reused.
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


# Custom patterns for assessment-specific sensitive fields.
PASSWORD_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd)\s*[:=]\s*([^\s,;]+)"
)

CLIENT_ID_PATTERN = re.compile(
    r"(?i)\b(client[\s_-]*id)\s*[:=]\s*([A-Za-z0-9_-]+)"
)


def mask_custom_sensitive_data(text: str) -> str:
    """Mask passwords and client IDs using custom regex rules."""

    text = PASSWORD_PATTERN.sub(
        lambda match: f"{match.group(1)}: <PASSWORD>",
        text,
    )

    text = CLIENT_ID_PATTERN.sub(
        lambda match: f"{match.group(1)}: <CLIENT_ID>",
        text,
    )

    return text


def mask_pii(text: str) -> str:
    """
    Detect and mask sensitive information.

    Handles common PII using Microsoft Presidio and
    assessment-specific fields using custom regex rules.
    """

    if not text or not text.strip():
        return text

    # First protect custom sensitive fields.
    masked_text = mask_custom_sensitive_data(text)

    # Detect common PII.
    results = analyzer.analyze(
        text=masked_text,
        language="en",
        entities=[
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "PERSON",
            "CREDIT_CARD",
            "IP_ADDRESS",
        ],
    )

    operators = {
        "EMAIL_ADDRESS": OperatorConfig(
            "replace",
            {"new_value": "<EMAIL_ADDRESS>"},
        ),
        "PHONE_NUMBER": OperatorConfig(
            "replace",
            {"new_value": "<PHONE_NUMBER>"},
        ),
        "PERSON": OperatorConfig(
            "replace",
            {"new_value": "<PERSON>"},
        ),
        "CREDIT_CARD": OperatorConfig(
            "replace",
            {"new_value": "<CREDIT_CARD>"},
        ),
        "IP_ADDRESS": OperatorConfig(
            "replace",
            {"new_value": "<IP_ADDRESS>"},
        ),
    }

    anonymized = anonymizer.anonymize(
        text=masked_text,
        analyzer_results=results,
        operators=operators,
    )

    return anonymized.text