import json
from pathlib import Path

DATASET_PATH = Path(__file__).parents[2] / "eval" / "rag_cases.json"


def test_rag_dataset_has_one_hundred_synthetic_cases_and_review_contract() -> None:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    cases = dataset["cases"]
    contract = dataset["case_contract"]

    assert dataset["fixture_kind"] == "synthetic_non_copyrighted_flexcube_style"
    assert len(cases) == 100
    assert len({case["case_id"] for case in cases}) == 100
    assert set(contract["required_fields"]) >= {
        "case_id",
        "category",
        "question",
        "answerability",
        "expected_evidence",
        "supported_status",
        "relevant_sections",
        "answer_type",
        "citation_expectation",
    }
    assert dataset["review_protocol"]["reviewers_required"] == 2
    assert dataset["review_protocol"]["disagreement_resolution"] == "adjudication"
    assert ">= 0.90" in dataset["review_protocol"]["sc_pass_rule"]


def test_rag_dataset_contract_resolves_expectations_for_every_case() -> None:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    cases = dataset["cases"]
    resolution = dataset["case_contract"]["expectation_resolution"]
    case_ids = {case["case_id"] for case in cases}

    for case in cases:
        answerability = case["answerability"]
        assert case["question"]
        assert answerability in resolution["supported_status"]
        assert answerability in resolution["answer_type"]
        assert answerability in resolution["citation_expectation"]
        expected_evidence = [] if answerability == "unanswerable" else [
            f"synthetic/{case['category']}"
        ]
        expected_status = resolution["supported_status"][answerability]
        expected_answer_type = resolution["category_answer_type_overrides"].get(
            case["category"], resolution["answer_type"][answerability]
        )
        expected_citation = resolution["citation_expectation"][answerability]
        resolved = {
            "expected_evidence": expected_evidence,
            "supported_status": expected_status,
            "relevant_sections": [f"synthetic/{case['category']}"],
            "answer_type": expected_answer_type,
            "citation_expectation": expected_citation,
        }
        assert resolved["expected_evidence"] == expected_evidence
        assert resolved["supported_status"] in {"supported", "partially_supported", "unsupported"}
        assert resolved["relevant_sections"] == [f"synthetic/{case['category']}"]
        assert resolved["answer_type"] in {"GROUNDED", "PARTIAL", "INSUFFICIENT", "AMBIGUOUS"}
        assert resolved["citation_expectation"] in {
            "required",
            "required_for_supported_claims",
            "none",
        }

    for examples in dataset["coverage_examples"].values():
        assert set(examples) <= case_ids
    assert set(dataset["coverage_categories"]) >= {
        "citation",
        "infrastructure_failure",
        "partial_answer",
        "injection",
        "unsupported",
    }
