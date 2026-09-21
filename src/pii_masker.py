"""
PII masking for anything that's about to be embedded and stored.

Two passes run back to back: a small set of custom regexes catch structured,
labeled secrets (passwords, API keys, card/account numbers, Aadhaar/PAN
numbers) that regex is genuinely the right tool for, since they follow a
predictable "label: value" shape. Microsoft Presidio then handles the fuzzier,
NLP-driven stuff — person names, locations, emails, phone numbers — where you
actually need real entity recognition rather than a pattern. This all runs on
the raw document text before it ever gets chunked or embedded, so nothing
sensitive makes it into the vector store.
"""

import re

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Presidio engines are created once and reused.
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


# Custom sensitive-data patterns

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


# Runs one regex pattern against the text and replaces only the value part with a placeholder, keeping the field label as is.
# So "password: hunter2" becomes "password: <PASSWORD>" instead of losing the label entirely.
def _replace_labeled_value(
    text: str,
    pattern: re.Pattern,
    placeholder: str,
) -> str:
    return pattern.sub(
        lambda match: f"{match.group(1)}: {placeholder}",
        text,
    )


# Runs every custom regex pattern (password, API key, secret, Aadhaar, PAN, bank account, etc.) over the text one by one.
# Each match gets replaced with its own typed placeholder like <PASSWORD> or <AADHAAR_NUMBER>.
def mask_custom_sensitive_data(text: str) -> str:
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


# Masks all sensitive info in a piece of text before it gets embedded and stored: custom secrets first, then Presidio for names, emails, phone numbers, etc.
# This must run on the full document text before it is chunked, otherwise a sensitive value could get cut in half at a chunk boundary and only partly masked.
def mask_pii(text: str) -> str:
    if not text or not text.strip():
        return text

    # Step 1: Mask custom secrets and identifiers first. These follow a
    # predictable "label: value" shape that Presidio has no built-in concept
    # of, so a plain regex pass is more reliable here than asking an NLP
    # model to recognize them. Doing this before Presidio also means Presidio
    # never even sees the raw secret — it's already replaced with a
    # placeholder — so there's no chance of a leftover fragment of a secret
    # getting mis-tagged and only partially redacted by the entity model.
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
        analyzer_results=results,  # type: ignore[arg-type]
        operators=operators,
    )

    return anonymized.text
