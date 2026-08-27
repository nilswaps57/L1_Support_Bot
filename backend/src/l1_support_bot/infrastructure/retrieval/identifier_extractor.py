"""Exact FLEXCUBE identifier extraction."""

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Identifiers:
    task_codes: tuple[str, ...] = ()
    error_codes: tuple[str, ...] = ()
    jira_ids: tuple[str, ...] = ()

    @property
    def all(self) -> tuple[str, ...]:
        return self.task_codes + self.error_codes + self.jira_ids


def extract_identifiers(text: str) -> Identifiers:
    task_codes = _unique(re.findall(r"\b[A-Z]{2,5}\d{3,5}\b", text.upper()))
    error_codes = _unique(re.findall(r"\b(?:ORA-\d+|ERR(?:OR)?[- ]?\d+|E-\d+)\b", text.upper()))
    jira_ids = _unique(re.findall(r"\b[A-Z][A-Z0-9]+-\d+\b", text.upper()))
    jira_ids = tuple(value for value in jira_ids if value not in error_codes)
    return Identifiers(task_codes, error_codes, jira_ids)


def _unique(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
