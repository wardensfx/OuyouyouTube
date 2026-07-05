from app.config import Settings


def test_allowed_google_emails_set_empty_by_default():
    assert Settings(allowed_google_emails="").allowed_google_emails_set == set()


def test_allowed_google_emails_set_parses_comma_separated_list():
    settings = Settings(allowed_google_emails="Alice@Example.com, bob@example.com ,, ")
    assert settings.allowed_google_emails_set == {"alice@example.com", "bob@example.com"}
