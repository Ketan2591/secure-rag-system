from src.pii_masker import mask_pii


# Checks that an email address in the text gets replaced with the <EMAIL_ADDRESS> placeholder and the real email is gone.
def test_email_masking():
    text = "Contact John at john@example.com"
    result = mask_pii(text)

    assert "john@example.com" not in result
    assert "<EMAIL_ADDRESS>" in result


# Checks that a phone number in the text gets replaced with the <PHONE_NUMBER> placeholder and the real number is gone.
def test_phone_masking():
    text = "Call me at +91 9876543210"
    result = mask_pii(text)

    assert "9876543210" not in result
    assert "<PHONE_NUMBER>" in result


# Checks that a labeled password value gets replaced with the <PASSWORD> placeholder and the real password is gone.
def test_password_masking():
    text = "Password: Secret123"
    result = mask_pii(text)

    assert "Secret123" not in result
    assert "<PASSWORD>" in result


# Checks that a labeled client ID gets replaced with the <CLIENT_ID> placeholder and the real ID is gone.
def test_client_id_masking():
    text = "Client ID: SECURE_CLIENT_2026"
    result = mask_pii(text)

    assert "SECURE_CLIENT_2026" not in result
    assert "<CLIENT_ID>" in result


# Checks that when several different PII types (email, phone, password, client ID) appear together in one text, all of them get masked at once.
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

# Checks that a labeled API key gets replaced with the <API_KEY> placeholder and the real key is gone.
def test_api_key_masking():
    text = "API Key: sk_test_ABC123XYZ789"
    result = mask_pii(text)

    assert "sk_test_ABC123XYZ789" not in result
    assert "<API_KEY>" in result


# Checks that a labeled client secret gets replaced with the <SECRET> placeholder and the real secret is gone.
def test_secret_masking():
    text = "Client Secret: SuperSecretValue123"
    result = mask_pii(text)

    assert "SuperSecretValue123" not in result
    assert "<SECRET>" in result


# Checks that a labeled access token gets replaced with the <ACCESS_TOKEN> placeholder and the real token is gone.
def test_access_token_masking():
    text = "Access Token: token_ABC123XYZ789"
    result = mask_pii(text)

    assert "token_ABC123XYZ789" not in result
    assert "<ACCESS_TOKEN>" in result


# Checks that a labeled bank account number gets replaced with the <BANK_ACCOUNT> placeholder and the real number is gone.
def test_bank_account_masking():
    text = "Bank Account: 123456789012"
    result = mask_pii(text)

    assert "123456789012" not in result
    assert "<BANK_ACCOUNT>" in result


# Checks that a labeled Aadhaar number gets replaced with the <AADHAAR_NUMBER> placeholder and the real number is gone.
def test_aadhaar_masking():
    text = "Aadhaar Number: 1234 5678 9012"
    result = mask_pii(text)

    assert "1234 5678 9012" not in result
    assert "<AADHAAR_NUMBER>" in result


# Checks that a labeled PAN number gets replaced with the <PAN_NUMBER> placeholder and the real number is gone.
def test_pan_masking():
    text = "PAN Number: ABCDE1234F"
    result = mask_pii(text)

    assert "ABCDE1234F" not in result
    assert "<PAN_NUMBER>" in result