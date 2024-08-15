# Glov-RAG

> ## RAG Based Question-Answer System

Glov-rag is a question-answering system based on an pretrained embedding model SentenceTransformer: **BAAI/bge-m3**.
It uses **PGVector** as the vector database, stores splitted document chunks in the database, and allows users to query the database using a question.

## Features

- [x] Checks if url is a valid HTTP/HTTPS URL
- [x] Checks if url is a valid PDF URL
- [x] Checks PDF file size, configured to 20MB
- [x] Split PDF into chunks using PyMuPDF, each chunk size is between 80-100 words
- [x] Store splitted chunks in PGVector
- [x] Query PGVector using the query from incoming request
- [x] Logging on each step
- [x] Tests for downloading PDF file and splitting PDF into chunks

## Further Improvements

These are the improvements that can be done in the future; some of them are open to discussion and may vary based on the requirements.

- **Cache PDF files for consecutive requests, to avoid downloading the same file multiple times.**

  Caching the file submitted by the user can significantly reduce unnecessary downloads and improve performance. However, since there is no authentication mechanism in place, caching could introduce security risks, as it may expose sensitive information to unauthorized users.

- **Implement table extraction and image extraction from PDF files, to improve the quality of the extracted text.**

  Enhancing the extraction process by including table and image extraction will lead to more comprehensive and accurate results, especially when dealing with complex documents.

- **Accept pdf files from S3, Google Drive, and other cloud storage services.**

  Extending the system to accept PDF files from cloud storage services can provide more flexibility and convenience to users, allowing them to upload files from various sources.

- **Rate limit the incoming requests, to avoid abuse of the system.**

  Implementing a rate limit can help protect the system from being overwhelmed by excessive requests, potentially causing service disruptions. This can be achieved using FastAPI's rate limit middleware, which can efficiently manage and throttle incoming requests based on predefined limits.

- **Some constants are hard-coded, which can be moved to configuration files for better maintainability.**

  Constants such as the maximum file size, chunk size, and other configuration parameters can be moved to a configuration file, making it easier to manage and update these values without modifying the code.

## Installation

```bash
poetry install --with dev,test
```

## Usage (Local)

```bash
fastapi dev glov/app.py
```

## Build Docker Image

```bash
docker build -f docker/Dockerfile -t glov-rag .
```

## Run Docker Compose

```bash
docker compose -f docker/docker-compose.yml up -d
```

# Development

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.
All commits follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

Linting and formatting available using [pre-commit](https://pre-commit.com/).

To lint the code:

```bash
poe lint
```

Linting uses [ruff](https://github.com/astral-sh/ruff) and [mypy](https://mypy-lang.org/) for type checking.

To run tests:

```bash
poe test
```

## Why I Have Chosen PyMuPDFLoader?

I have benchmarked few PDF loaders from langchain with an example [PDF File (2.2MB 177 pages)](assets/FIA_2024_Formula_1_Technical_Regulations.pdf).

## The loaders are:

- PDFMinerLoader
- PyPDFLoader
- PyMuPDFLoader
- PDFPlumberLoader
- PyPDFium2Loader

I have chosen PyMuPDFLoader because it is the fastest among all the loaders.

![alt text](assets/pdf_loader_comparison.png)
