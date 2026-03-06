# LexiScan Auto

**Production-Grade Named Entity Recognition System for Legal Contract Parsing**

## Overview

LexiScan Auto is an intelligent document parsing system designed for high-volume law firms to automatically extract key entities from unstructured PDF contracts. The system combines OCR technology, deep learning NER models, and validation logic to deliver accurate, structured data extraction.

## Key Features

- 🔍 **Robust OCR Pipeline**: Converts scanned PDFs to clean, processable text using Tesseract
- 🧠 **Multi-Model NER**: Baseline (TF-IDF + Regex), Spacy Custom NER, and Bi-LSTM deep learning
- ✅ **Validation Layer**: Business logic for entity consistency and date validation
- 🚀 **Production API**: FastAPI REST endpoints with structured JSON output
- 🐳 **Containerized**: Docker-ready for easy deployment

## Extracted Entities

- **Parties**: Legal entity names (companies, individuals)
- **Dates**: Effective dates, termination dates, renewal terms
- **Amounts**: Monetary values and financial terms
- **Jurisdiction**: Governing law and legal jurisdictions
- **Terms**: Contract duration and renewal periods

## Project Structure

```
lexiscan-auto/
├── data/
│   ├── raw/                    # Original PDF contracts
│   ├── annotations/            # Annotated training data
│   └── processed/              # OCR-processed text
├── src/
│   ├── ocr/                    # OCR pipeline
│   ├── models/                 # NER models
│   │   ├── baseline/           # TF-IDF + Regex
│   │   ├── spacy_ner/          # Spacy custom NER
│   │   └── bilstm/             # Bi-LSTM model
│   ├── validation/             # Post-processing rules
│   ├── api/                    # FastAPI endpoints
│   └── utils/                  # Shared utilities
├── tests/                      # Unit and integration tests
├── notebooks/                  # Jupyter notebooks for exploration
├── configs/                    # Configuration files
└── docker/                     # Docker configuration

```

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Spacy model
python -m spacy download en_core_web_sm
```

### Usage

```python
from src.api.main import LexiScanAPI

# Initialize API
api = LexiScanAPI()

# Extract entities from PDF
result = api.extract_entities("path/to/contract.pdf")
print(result)
```

## Development Roadmap

- [x] Week 1: OCR Pipeline & Data Preparation
- [ ] Week 2: NER Model Development
- [ ] Week 3: Rule-Based Layer & Precision Enhancement
- [ ] Week 4: Containerization & Deployment

## Tech Stack

- **NLP/ML**: Spacy 3.7, TensorFlow 2.15, scikit-learn
- **OCR**: Tesseract, pdf2image, PyMuPDF
- **API**: FastAPI, Pydantic, Uvicorn
- **Deployment**: Docker, Docker Compose

## License

Proprietary - Infotact Solutions

## Contact

Data Science Engineering Track - Q4 2025
