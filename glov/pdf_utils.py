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

TWENTY_MB = 20971520


class PDFService:  # noqa: D101
    @staticmethod
    def download_pdf(url: str) -> str:
        """Download the PDF file from the given URL and save it to a temporary file."""
        try:
            logger.info("Starting PDF download from URL: %s", url)
            response = requests.get(str(url), timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
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
    def check_pdf_size(url: str, max_size: int = TWENTY_MB) -> None:
        """Check the size of the PDF file before downloading it."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            response.raise_for_status()
            pdf_size = int(response.headers.get("Content-Length", 0))
            if pdf_size == 0:
                logger.warning("Could not determine the size of the PDF file: %s", url)
            else:
                logger.info("PDF size: %s bytes", pdf_size)
            if pdf_size > max_size:
                logger.error("PDF file is too large: %s bytes", pdf_size)
                raise HTTPException(status_code=400, detail="PDF file is too large")
        except requests.RequestException as e:
            logger.exception("Failed to get PDF size: %s", url)
            raise HTTPException(status_code=400, detail=f"Failed to get PDF size: {e!s}") from e

    @staticmethod
    def validate_pdf_url(url: str) -> bool:
        """Check if the URL points to a PDF file."""
        logger.info("Validating PDF URL: %s", url)
        if not url.lower().endswith(".pdf"):
            logger.exception("The URL does not point to a PDF file: %s", url)
            raise HTTPException(status_code=400, detail="The URL does not point to a PDF file")
        return True
