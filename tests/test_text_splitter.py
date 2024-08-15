import pytest
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from test_pdf_service import download_pdf  # noqa: F401


@pytest.fixture
def loader(download_pdf):  # type: ignore[no-untyped-def] # noqa: F811
    """Fixture to load the PDF document using the downloaded PDF file."""
    return PyMuPDFLoader(download_pdf)


@pytest.fixture
def docs(loader):  # type: ignore[no-untyped-def]
    """Fixture to load documents from the PDF using the loader."""
    return loader.load()


@pytest.fixture
def text_splitter():  # type: ignore[no-untyped-def]
    """Fixture to create the text splitter with a chunk size of 100 words."""

    def word_count(text: str) -> int:
        """Count the number of words in the text."""
        return len(text.split())

    return RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, length_function=word_count)


def test_text_splitter(text_splitter, docs):  # type: ignore[no-untyped-def]
    """Test that the text splitter splits documents into approximately 100-word chunks."""
    all_splits = text_splitter.split_documents(docs)

    # Count words in each chunk and take average
    total_word_count = 0
    for split in all_splits:
        content = split.page_content
        word_count = len(content.split())
        total_word_count += word_count

    average_word_count = total_word_count / len(all_splits)

    # Check that the average word count is around 100
    assert (
        80 <= average_word_count <= 100
    ), f"Average word count is {average_word_count}, which is outside the expected range."


def test_exact_word_count(text_splitter, docs):  # type: ignore[no-untyped-def]
    """Test that the text splitter produces the expected number of words in the first chunk."""
    all_splits = text_splitter.split_documents(docs)
    content = all_splits[0].page_content
    word_count = len(content.split())

    # Check that the first chunk has around 100 words
    assert 80 <= word_count <= 100, f"First chunk has {word_count} words, which is outside the expected range."
