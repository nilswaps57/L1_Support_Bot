"""Parser-independent FLEXCUBE metadata extraction."""

from __future__ import annotations

import re
from collections.abc import Iterable

from l1_support_bot.domain.models.parsed_document import (
    DocumentElement,
    FlexcubeMetadata,
    ParseWarning,
)


class FlexcubeMetadataExtractor:
    _task_code = re.compile(r"\b[A-Z]{2,5}\d{3,5}\b")
    _error_code = re.compile(r"\b(?:ERR(?:OR)?[- ]?\d{2,6}|E[- ]?\d{2,6})\b", re.IGNORECASE)
    _jira = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
    _rca = re.compile(r"\bRCA[- ]?\d+\b", re.IGNORECASE)

    def extract(self, elements: Iterable[DocumentElement]) -> FlexcubeMetadata:
        texts = tuple(element.text for element in elements)
        task_codes = self._labelled_or_pattern(texts, r"task\s*code", self._task_code)
        screen_names = self._labelled_values(texts, r"screen\s*name")
        menu_paths = self._labelled_values(texts, r"menu\s*path")
        prerequisites = self._split_labelled(texts, r"prerequisites?")
        modes = self._split_labelled(texts, r"modes?")
        field_names = self._split_labelled(texts, r"fields?")
        procedure_steps = tuple(
            match.group(1).strip()
            for text in texts
            for match in re.finditer(r"(?:step\s*\d+|\d+[.)])\s*[:.-]?\s*(.+)", text, re.IGNORECASE)
        )
        error_codes = self._labelled_or_pattern(texts, r"error\s*code", self._error_code)
        jira_ids = self._unique(
            value.upper()
            for text in texts
            for value in self._jira.findall(text)
            if not value.upper().startswith("RCA-")
        )
        rca_references = self._unique(
            value.upper().replace(" ", "-") for text in texts for value in self._rca.findall(text)
        )
        diagnostics: list[ParseWarning] = []
        for label, values in (
            ("task code", task_codes),
            ("screen name", screen_names),
            ("menu path", menu_paths),
        ):
            if len(values) > 1:
                diagnostics.append(
                    ParseWarning(
                        "metadata",
                        (
                            f"The source contains conflicting {label} values; "
                            "all values were preserved."
                        ),
                        code="SOURCE_INCONSISTENCY",
                    )
                )
        return FlexcubeMetadata(
            task_codes=task_codes,
            screen_names=screen_names,
            menu_paths=menu_paths,
            prerequisites=prerequisites,
            modes=modes,
            field_names=field_names,
            procedure_steps=procedure_steps,
            error_codes=error_codes,
            jira_ids=jira_ids,
            rca_references=rca_references,
            diagnostics=tuple(diagnostics),
        )

    @staticmethod
    def _labelled_values(texts: tuple[str, ...], label: str) -> tuple[str, ...]:
        return FlexcubeMetadataExtractor._unique(
            match.group(1).strip(" :-")
            for text in texts
            for match in re.finditer(rf"{label}\s*[:=-]\s*(.+)", text, re.IGNORECASE)
        )

    @staticmethod
    def _split_labelled(texts: tuple[str, ...], label: str) -> tuple[str, ...]:
        values = FlexcubeMetadataExtractor._labelled_values(texts, label)
        return FlexcubeMetadataExtractor._unique(
            item.strip(" .")
            for value in values
            for item in re.split(r",|;|\n", value)
            if item.strip()
        )

    @staticmethod
    def _labelled_or_pattern(
        texts: tuple[str, ...], label: str, pattern: re.Pattern[str]
    ) -> tuple[str, ...]:
        labelled = FlexcubeMetadataExtractor._labelled_values(texts, label)
        values = (
            value
            for text in texts
            for line in text.splitlines()
            if not re.match(
                r"\s*(?:prerequisites?|fields?|modes?|screen\s*name|menu\s*path)\s*:",
                line,
                re.IGNORECASE,
            )
            for value in pattern.findall(line)
        )
        return FlexcubeMetadataExtractor._unique((*labelled, *values))

    @staticmethod
    def _unique(values: Iterable[str]) -> tuple[str, ...]:
        result: list[str] = []
        for value in values:
            clean = value.strip()
            if clean and clean not in result:
                result.append(clean)
        return tuple(result)
