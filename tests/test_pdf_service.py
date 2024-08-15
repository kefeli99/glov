from glov.pdf_utils import PDFService

PDF_URL = "https://www.fia.com/sites/default/files/fia_2024_formula_1_technical_regulations_-_issue_1_-_2023-04-25.pdf"


def test_download_pdf() -> None:
    pdf_path = PDFService.download_pdf(PDF_URL)
    assert pdf_path.endswith(".pdf")


def test_validate_pdf_url() -> None:
    assert PDFService.validate_pdf_url(PDF_URL) is True
