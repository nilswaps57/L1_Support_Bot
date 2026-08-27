from l1_support_bot.domain.models.parsed_document import DocumentElement
from l1_support_bot.infrastructure.parsing.flexcube_metadata_extractor import (
    FlexcubeMetadataExtractor,
)


def test_extracts_flexcube_identifiers_and_operational_metadata() -> None:
    element = DocumentElement(
        element_type="procedure",
        text=(
            "Task Code: BA435\nScreen Name: Customer Account\n"
            "Menu Path: Main > Customer > Account\n"
            "Prerequisites: ST001, ST002\nModes: Inquiry, Modify\nFields: Customer ID, Account No\n"
            "Step 1: Select the customer\nError Code: E-102\nJIRA: JIRA-1234\nRCA: RCA-77"
        ),
        page_number=7,
        section_path=("Accounts", "BA435"),
    )

    metadata = FlexcubeMetadataExtractor().extract((element,))

    assert metadata.task_codes == ("BA435",)
    assert metadata.screen_names == ("Customer Account",)
    assert metadata.menu_paths == ("Main > Customer > Account",)
    assert metadata.prerequisites == ("ST001", "ST002")
    assert metadata.modes == ("Inquiry", "Modify")
    assert metadata.field_names == ("Customer ID", "Account No")
    assert metadata.procedure_steps == ("Select the customer",)
    assert metadata.error_codes == ("E-102",)
    assert metadata.jira_ids == ("JIRA-1234",)
    assert metadata.rca_references == ("RCA-77",)


def test_conflicting_source_values_are_diagnostics_not_corrections() -> None:
    elements = (
        DocumentElement(element_type="paragraph", text="Task Code: BA435"),
        DocumentElement(element_type="paragraph", text="Task Code: BA436"),
    )

    metadata = FlexcubeMetadataExtractor().extract(elements)

    assert metadata.task_codes == ("BA435", "BA436")
    assert metadata.diagnostics
    assert "conflicting" in metadata.diagnostics[0].description.lower()
