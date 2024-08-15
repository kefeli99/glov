from collections.abc import Iterator
from pathlib import Path

import pytest
from glov.pdf_utils import PDFService

PDF_URL = "https://www.fia.com/sites/default/files/fia_2024_formula_1_technical_regulations_-_issue_1_-_2023-04-25.pdf"


@pytest.fixture(scope="module")
def download_pdf() -> Iterator[str]:
    """Fixture to download the PDF file and ensure it's present."""
    PDFService.validate_pdf_url(PDF_URL)
    pdf_path = PDFService.download_pdf(PDF_URL)
    yield pdf_path
    # Cleanup after tests
    Path(pdf_path).unlink()


def test_pdf_is_downloaded(download_pdf) -> None:  # type: ignore[no-untyped-def]
    """Test that the PDF is downloaded and is a valid file."""
    pdf_path = download_pdf
    assert Path(pdf_path).exists(), "The PDF file was not downloaded."
    assert Path(pdf_path).is_file(), "The downloaded PDF path is not a file."
