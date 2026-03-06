# API Documentation

## LexiScan Auto REST API

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required (add JWT/API keys for production)

---

## Endpoints

### 1. Root Endpoint

**GET /**

Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to LexiScan Auto API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 2. Health Check

**GET /health**

Check API health and model loading status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "baseline": true,
    "date_validator": true,
    "entity_validator": true
  }
}
```

---

### 3. Extract Entities

**POST /extract**

Extract entities from uploaded contract document.

**Parameters:**
- `file` (form-data, required): PDF or TXT contract file
- `model` (query, optional): NER model to use (`baseline`, `spacy`, `bilstm`)
  - Default: `baseline`

**Request Example (cURL):**
```bash
curl -X POST "http://localhost:8000/extract?model=baseline" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.txt"
```

**Request Example (Python):**
```python
import requests

url = "http://localhost:8000/extract"
files = {"file": open("contract.txt", "rb")}
params = {"model": "baseline"}

response = requests.post(url, files=files, params=params)
print(response.json())
```

**Response Schema:**
```json
{
  "document_id": "string",
  "entities": {
    "PARTY": [
      {
        "text": "string",
        "label": "PARTY",
        "start": 0,
        "end": 0,
        "confidence": 0.0,
        "method": "string"
      }
    ],
    "DATE": [...],
    "AMOUNT": [...],
    "JURISDICTION": [...],
    "TERM": [...]
  },
  "dates": {
    "effective_date": {
      "text": "string",
      "iso": "2024-01-01",
      "confidence": 0.0
    },
    "termination_date": {...},
    "expiration_date": {...}
  },
  "validation_status": "PASSED|WARNING|FAILED",
  "validation_errors": ["string"],
  "validation_warnings": ["string"],
  "processing_time_ms": 0.0,
  "model_used": "string"
}
```

**Success Response Example:**
```json
{
  "document_id": "sample_contract.txt",
  "entities": {
    "PARTY": [
      {
        "text": "Acme Corporation",
        "label": "PARTY",
        "start": 45,
        "end": 61,
        "confidence": 0.9,
        "method": "regex"
      },
      {
        "text": "Beta LLC",
        "label": "PARTY",
        "start": 120,
        "end": 128,
        "confidence": 0.85,
        "method": "regex"
      }
    ],
    "DATE": [
      {
        "text": "January 1, 2024",
        "label": "DATE",
        "start": 200,
        "end": 215,
        "confidence": 0.95,
        "method": "regex"
      }
    ],
    "AMOUNT": [
      {
        "text": "$500,000",
        "label": "AMOUNT",
        "start": 350,
        "end": 358,
        "confidence": 0.9,
        "method": "regex"
      }
    ],
    "JURISDICTION": [
      {
        "text": "State of California",
        "label": "JURISDICTION",
        "start": 450,
        "end": 469,
        "confidence": 0.85,
        "method": "regex"
      }
    ]
  },
  "dates": {
    "effective_date": {
      "text": "January 1, 2024",
      "iso": "2024-01-01",
      "confidence": 0.95
    }
  },
  "validation_status": "PASSED",
  "validation_errors": [],
  "validation_warnings": [],
  "processing_time_ms": 1250.5,
  "model_used": "baseline"
}
```

**Error Response (400 - Bad Request):**
```json
{
  "error": "Only PDF and TXT files are supported",
  "detail": null
}
```

**Error Response (500 - Internal Server Error):**
```json
{
  "error": "Internal server error",
  "detail": "Error message details"
}
```

---

## Entity Types

| Label | Description | Example |
|-------|-------------|---------|
| `PARTY` | Legal entity names (companies, individuals) | "Acme Corporation", "John Doe" |
| `DATE` | Dates (effective, termination, expiration) | "January 1, 2024", "01/01/2024" |
| `AMOUNT` | Monetary values | "$500,000", "USD 1,000,000" |
| `JURISDICTION` | Governing law, legal jurisdictions | "State of California", "New York" |
| `TERM` | Contract duration, renewal terms | "3 years", "successive 1 year" |

---

## Validation Rules

### Date Consistency
- Termination date must be after effective date
- Expiration date must be after effective date
- Dates must be within reasonable range (1900-2126)

### Entity Validation
- Party names must be at least 3 characters
- Amounts must have valid numeric values
- No overlapping entities allowed

### Validation Status
- `PASSED`: All validations successful
- `WARNING`: Minor issues detected (e.g., missing jurisdiction)
- `FAILED`: Critical validation errors (e.g., date inconsistency)

---

## Rate Limiting

Currently no rate limiting (add for production deployment)

**Recommended limits:**
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Interactive Documentation

Visit the following URLs for interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid file type, missing parameters) |
| 422 | Validation Error (invalid request format) |
| 500 | Internal Server Error |

---

## Best Practices

1. **File Size:** Keep files under 10MB for optimal performance
2. **File Format:** Use TXT files for faster processing (PDF requires OCR)
3. **Model Selection:** 
   - Use `baseline` for speed
   - Use `spacy` for better accuracy (when trained)
   - Use `bilstm` for state-of-the-art results (when trained)
4. **Error Handling:** Always check `validation_status` and `validation_errors`
5. **Batch Processing:** For multiple files, consider parallel requests

---

## Example Integration

### Python Client
```python
import requests
from pathlib import Path

class LexiScanClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def extract_entities(self, file_path, model="baseline"):
        url = f"{self.base_url}/extract"
        files = {"file": open(file_path, "rb")}
        params = {"model": model}
        
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self):
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()

# Usage
client = LexiScanClient()
result = client.extract_entities("contract.txt")

print(f"Found {len(result['entities'])} entity types")
print(f"Validation: {result['validation_status']}")
```

---

## Support

For issues or questions:
- Check logs at `logs/api.log`
- Review error messages in response
- Consult walkthrough documentation
