from l1_support_bot.interface.config import Settings


def test_settings_have_safe_local_defaults() -> None:
    settings = Settings()

    assert settings.app_version == "0.1.0"
    assert settings.database_url.startswith("sqlite")
    assert settings.max_request_body_bytes > 0
    assert settings.cors_allowed_origins == ["http://localhost:5173"]


def test_settings_do_not_model_secret_values() -> None:
    settings = Settings()

    assert not hasattr(settings, "api_key")
    assert not hasattr(settings, "password")