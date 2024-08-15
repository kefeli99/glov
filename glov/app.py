"""API for extracting text from a PDF file and generating embeddings using a Hugging Face model."""

import logging
from pathlib import Path

from fastapi import Depends, FastAPI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

from glov.pdf_utils import PDFService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
DB_CONNECTION = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
COLLECTION_NAME = "my_docs"
EMBEDDINGS_MODEL_NAME = "BAAI/bge-m3"
MIN_QUERY_LENGTH = 3

app = FastAPI(
    title="Glov Query API",
    description="API for extracting text from a PDF file and generating embeddings using a Hugging Face model",
    version="0.1.0",
    contact={"name": "Osman Dogukan Kefeli", "email": "dogukankefeli@gmail.com"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
)

embeddings_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")


def get_vectorstore() -> PGVector:  # noqa: D103
    logger.info("Initializing vector store with model: %s", EMBEDDINGS_MODEL_NAME)
    embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
    return PGVector(
        embeddings=embeddings_model,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )


def word_count(text: str) -> int:
    """Count the number of words in the text."""
    return len(text.split())


class TextService:  # noqa: D101
    @staticmethod
    def split_text(docs: list[Document]) -> list[Document]:
        """Split the text into chunks using the defined text splitter."""
        logger.info("Splitting text into chunks")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, length_function=word_count)
        splits = text_splitter.split_documents(docs)
        logger.info("Text successfully split into %d chunks", len(splits))
        return splits


class QueryRequest(BaseModel):  # noqa: D101
    url: HttpUrl  # Validates that the input is a valid URL
    query: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://www.fia.com/sites/default/files/fia_2024_formula_1_technical_regulations_-_issue_1_-_2023-04-25.pdf",
                "query": "What are the rules for brakes?",
            }
        },
    )

    @field_validator("query")
    @classmethod
    def check_query_length(cls, value: str) -> str:
        """Check that the query is at least 3 characters long."""
        if len(value) < MIN_QUERY_LENGTH:
            msg = "Query must be at least 3 characters long"
            raise ValueError(msg)
        return value


class QueryResponse(BaseModel):  # noqa: D101
    chunks: list[str]


@app.post("/embed/", response_model=QueryResponse)
def query_pdf(request: QueryRequest, vectorstore=Depends(get_vectorstore)):  # type: ignore[no-untyped-def]
    """Extract text from a PDF file and generate embeddings for the text."""
    logger.info("Received query PDF request with URL: %s", request.url)
    url = str(request.url)
    # Validate the PDF URL
    PDFService.validate_pdf_url(url)
    # Download the PDF file
    pdf_path = PDFService.download_pdf(url)

    try:
        # Load the PDF file
        logger.info("Loading PDF from path: %s", pdf_path)
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        # Split the text into chunks
        all_splits = TextService.split_text(docs)

        # Add the documents to the vector store
        logger.info("Adding %d document chunks to the vector store", len(all_splits))
        vectorstore.add_documents(all_splits, ids=list(range(len(all_splits))))

        # Perform a similarity search
        logger.info("Performing similarity search with query: %s", request.query)
        results = vectorstore.similarity_search_with_score(query=request.query, k=5)

        logger.info("Returning %d results from similarity search", len(results))
        return QueryResponse(chunks=[doc.page_content for doc, _ in results])
    finally:
        # Always remove the temporary PDF file
        logger.info("Cleaning up temporary PDF file: %s", pdf_path)
        Path(pdf_path).unlink()


if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
