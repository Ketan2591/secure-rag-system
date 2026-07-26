import re

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Presidio engines are created once and reused.
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


# -------------------------------------------------------------------
# Custom sensitive-data patterns
# -------------------------------------------------------------------

PASSWORD_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd)\s*[:=]\s*([^\s,;]+)"
)

CLIENT_ID_PATTERN = re.compile(
    r"(?i)\b(client[\s_-]*id)\s*[:=]\s*([A-Za-z0-9_.-]+)"
)

API_KEY_PATTERN = re.compile(
    r"(?i)\b(api[\s_-]*key|apikey)\s*[:=]\s*([^\s,;]+)"
)

SECRET_PATTERN = re.compile(
    r"(?i)\b(client[\s_-]*secret|secret[\s_-]*key|secret)\s*[:=]\s*([^\s,;]+)"
)

ACCESS_TOKEN_PATTERN = re.compile(
    r"(?i)\b(access[\s_-]*token|auth[\s_-]*token|bearer[\s_-]*token)\s*[:=]\s*([^\s,;]+)"
)

BANK_ACCOUNT_PATTERN = re.compile(
    r"(?i)\b(account[\s_-]*(?:number|no|#)|bank[\s_-]*account)"
    r"\s*[:=]\s*([A-Za-z0-9-]{6,34})"
)

AADHAAR_PATTERN = re.compile(
    r"(?i)\b(aadhaar|aadhar)(?:[\s_-]*(?:number|no))?"
    r"\s*[:=]\s*(\d{4}[\s-]?\d{4}[\s-]?\d{4})"
)

PAN_PATTERN = re.compile(
    r"(?i)\b(pan)(?:[\s_-]*(?:number|no))?"
    r"\s*[:=]\s*([A-Z]{5}[0-9]{4}[A-Z])"
)


def _replace_labeled_value(
    text: str,
    pattern: re.Pattern,
    placeholder: str,
) -> str:
    """Preserve the field label while replacing its sensitive value."""

    return pattern.sub(
        lambda match: f"{match.group(1)}: {placeholder}",
        text,
    )


def mask_custom_sensitive_data(text: str) -> str:
    """Mask application secrets and additional sensitive identifiers."""

    patterns = [
        (PASSWORD_PATTERN, "<PASSWORD>"),
        (CLIENT_ID_PATTERN, "<CLIENT_ID>"),
        (API_KEY_PATTERN, "<API_KEY>"),
        (SECRET_PATTERN, "<SECRET>"),
        (ACCESS_TOKEN_PATTERN, "<ACCESS_TOKEN>"),
        (BANK_ACCOUNT_PATTERN, "<BANK_ACCOUNT>"),
        (AADHAAR_PATTERN, "<AADHAAR_NUMBER>"),
        (PAN_PATTERN, "<PAN_NUMBER>"),
    ]

    for pattern, placeholder in patterns:
        text = _replace_labeled_value(
            text=text,
            pattern=pattern,
            placeholder=placeholder,
        )

    return text


def mask_pii(text: str) -> str:
    """
    Detect and mask sensitive information before embedding/storage.

    Custom security-sensitive values are masked first.
    Microsoft Presidio is then used for common PII.

    The original sensitive values must never be stored in ChromaDB.
    """

    if not text or not text.strip():
        return text

    # Step 1: Mask custom secrets and identifiers first.
    masked_text = mask_custom_sensitive_data(text)

    # Step 2: Detect common PII using Presidio.
    results = analyzer.analyze(
        text=masked_text,
        language="en",
        entities=[
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "PERSON",
            "CREDIT_CARD",
            "IP_ADDRESS",
            "LOCATION",
            "IBAN_CODE",
            "US_SSN",
        ],
    )

    # Step 3: Replace detected values with typed placeholders.
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
        "LOCATION": OperatorConfig(
            "replace",
            {"new_value": "<LOCATION>"},
        ),
        "IBAN_CODE": OperatorConfig(
            "replace",
            {"new_value": "<IBAN_CODE>"},
        ),
        "US_SSN": OperatorConfig(
            "replace",
            {"new_value": "<SSN>"},
        ),
    }

    anonymized = anonymizer.anonymize(
        text=masked_text,
        analyzer_results=results,
        operators=operators,
    )

    return anonymized.text