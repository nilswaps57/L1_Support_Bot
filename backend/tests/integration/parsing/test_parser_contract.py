import pytest

from l1_support_bot.domain.models.document import FileType
from l1_support_bot.infrastructure.parsing.docling_parser import DoclingParser
from l1_support_bot.infrastructure.parsing.pymupdf_parser import PyMuPDFParser
from l1_support_bot.infrastructure.parsing.python_docx_parser import PythonDocxParser


def test_markdown_parser_preserves_headings_lists_and_flexcube_text() -> None:
    document = DoclingParser().parse_markdown(
        b"# BA435\n\n- Open the screen\n- Select Authorize\n\n> Note: use inquiry mode."
    )

    assert document.elements[0].element_type == "heading"
    assert document.elements[0].text == "BA435"
    assert any(element.element_type == "list" for element in document.elements)
    assert "inquiry mode" in document.text


@pytest.mark.asyncio
async def test_pdf_fallback_preserves_page_numbers() -> None:
    parser = PyMuPDFParser()
    pdf = parser.make_test_pdf("BA435\nScreen Name: Customer Account")

    document = await parser.parse(pdf, FileType.PDF)

    assert document.elements
    assert all(element.page_number == 1 for element in document.elements)
    assert "BA435" in document.text


@pytest.mark.asyncio
async def test_docx_fallback_preserves_heading_and_table() -> None:
    parser = PythonDocxParser()
    document = await parser.parse(parser.make_test_docx("BA435", "Customer Account"), FileType.DOCX)

    assert any(element.element_type == "heading" for element in document.elements)
    assert any(element.element_type == "table" for element in document.elements)
    assert document.elements[-1].page_number is None


@pytest.mark.asyncio
async def test_unreadable_input_has_safe_parser_error() -> None:
    parser = PyMuPDFParser()

    try:
        await parser.parse(b"not a pdf", FileType.PDF)
    except Exception as error:
        assert "traceback" not in str(error).lower()
        assert "/home/" not in str(error)
    else:
        raise AssertionError("Unreadable PDF must fail")
