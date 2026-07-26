from src.pii_masker import mask_pii


def test_email_masking():
    text = "Contact John at john@example.com"
    result = mask_pii(text)

    assert "john@example.com" not in result
    assert "<EMAIL_ADDRESS>" in result


def test_phone_masking():
    text = "Call me at +91 9876543210"
    result = mask_pii(text)

    assert "9876543210" not in result
    assert "<PHONE_NUMBER>" in result


def test_password_masking():
    text = "Password: Secret123"
    result = mask_pii(text)

    assert "Secret123" not in result
    assert "<PASSWORD>" in result


def test_client_id_masking():
    text = "Client ID: SECURE_CLIENT_2026"
    result = mask_pii(text)

    assert "SECURE_CLIENT_2026" not in result
    assert "<CLIENT_ID>" in result


def test_multiple_pii_masking():
    text = """
    HR Email: hr@company.com
    HR Phone: +91 9876543210
    Password: InternalSecret123
    Client ID: SECURE_CLIENT_2026
    """

    result = mask_pii(text)

    assert "hr@company.com" not in result
    assert "9876543210" not in result
    assert "InternalSecret123" not in result
    assert "SECURE_CLIENT_2026" not in result

def test_api_key_masking():
    text = "API Key: sk_test_ABC123XYZ789"
    result = mask_pii(text)

    assert "sk_test_ABC123XYZ789" not in result
    assert "<API_KEY>" in result


def test_secret_masking():
    text = "Client Secret: SuperSecretValue123"
    result = mask_pii(text)

    assert "SuperSecretValue123" not in result
    assert "<SECRET>" in result


def test_access_token_masking():
    text = "Access Token: token_ABC123XYZ789"
    result = mask_pii(text)

    assert "token_ABC123XYZ789" not in result
    assert "<ACCESS_TOKEN>" in result


def test_bank_account_masking():
    text = "Bank Account: 123456789012"
    result = mask_pii(text)

    assert "123456789012" not in result
    assert "<BANK_ACCOUNT>" in result


def test_aadhaar_masking():
    text = "Aadhaar Number: 1234 5678 9012"
    result = mask_pii(text)

    assert "1234 5678 9012" not in result
    assert "<AADHAAR_NUMBER>" in result


def test_pan_masking():
    text = "PAN Number: ABCDE1234F"
    result = mask_pii(text)

    assert "ABCDE1234F" not in result
    assert "<PAN_NUMBER>" in result