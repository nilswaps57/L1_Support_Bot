from pathlib import Path

ROOT = Path(__file__).parents[2] / "src" / "l1_support_bot"


def test_domain_and_application_do_not_import_frameworks_or_adapters() -> None:
    forbidden = (
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "qdrant",
        "ollama",
        "tool_execution",
        "sql_execution",
        "shell_command",
        "jira_mutation",
        "flexcube_mutation",
    )
    for layer in ("domain", "application"):
        for source_file in (ROOT / layer).rglob("*.py"):
            source = source_file.read_text()
            assert not any(term in source.lower() for term in forbidden), source_file


def test_domain_ports_are_capabilities_only() -> None:
    ports_source = "\n".join(
        source_file.read_text() for source_file in (ROOT / "domain" / "ports").rglob("*.py")
    )
    assert "execute" not in ports_source.lower()