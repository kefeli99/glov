"""Utility functions for downloading and validating PDF files."""

import logging
import tempfile

import requests
from fastapi import HTTPException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30


class PDFService:  # noqa: D101
    @staticmethod
    def download_pdf(url: str) -> str:
        """Download the PDF file from the given URL and save it to a temporary file."""
        try:
            logger.info("Starting PDF download from URL: %s", url)
            response = requests.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            response.raise_for_status()
        except requests.Timeout as e:
            logger.exception("PDF download timed out: %s", url)
            raise HTTPException(status_code=408, detail="Request to download the PDF timed out") from e
        except requests.RequestException as e:
            logger.exception("Failed to download the PDF from URL: %s", url)
            raise HTTPException(status_code=400, detail=f"Failed to download the PDF: {e!s}") from e

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(response.content)
            logger.info("PDF successfully downloaded and saved to: %s", temp_pdf.name)
            return temp_pdf.name

    @staticmethod
    def validate_pdf_url(url: HttpUrl) -> bool:
        """Check if the URL points to a PDF file."""
        logger.info("Validating PDF URL: %s", url)
        if not url.path:
            raise HTTPException(status_code=400, detail="The URL does not point to a PDF file")
        if not url.path.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="The URL does not point to a PDF file")
        return True
