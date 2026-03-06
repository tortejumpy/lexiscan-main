"""
FastAPI Main Application
LexiScan Auto REST API
"""

import logging
import time
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .schemas import ExtractionResponse, HealthResponse, ErrorResponse, EntityResponse, DateInfo
from ..models.baseline import BaselineNERModel
from ..validation import DateValidator, EntityValidator
from ..utils.helpers import setup_logging
from ..ocr.pdf_processor import PDFProcessor

# Setup logging
setup_logging(log_file='logs/api.log', log_level='INFO')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LexiScan Auto API",
    description="Production-Grade Legal Document NER System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve demo_frontend as static files if the folder exists
_frontend_dir = Path(__file__).parent.parent.parent / "demo_frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the demo frontend"""
    index_file = _frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>LexiScan Auto API</h1><p>Visit <a href='/docs'>/docs</a></p>")

# Global model instances
baseline_model = None
date_validator = None
entity_validator = None
pdf_processor = None


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global baseline_model, date_validator, entity_validator, pdf_processor
    
    logger.info("Initializing LexiScan Auto API...")
    
    try:
        # Initialize models
        baseline_model = BaselineNERModel()
        date_validator = DateValidator()
        entity_validator = EntityValidator()
        pdf_processor = PDFProcessor(dpi=200)  # 200 DPI is fast and sufficient for text PDFs
        
        logger.info("All models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise




@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={
            "baseline": baseline_model is not None,
            "date_validator": date_validator is not None,
            "entity_validator": entity_validator is not None
        }
    )


@app.post("/extract", response_model=ExtractionResponse)
async def extract_entities(
    file: UploadFile = File(..., description="PDF or TXT contract file"),
    model: str = Query("baseline", description="Model to use (baseline, spacy, bilstm)")
):
    """
    Extract entities from uploaded contract document
    
    Args:
        file: Uploaded PDF or TXT file
        model: NER model to use
        
    Returns:
        Extraction results with entities and validation
    """
    start_time = time.time()
    
    try:
        # Validate file type (case-insensitive: .PDF, .TXT etc. all accepted)
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
        
        # Read file content
        content = await file.read()
        filename_lower = file.filename.lower()
        
        # For TXT files, decode directly
        if filename_lower.endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
        elif filename_lower.endswith('.pdf'):
            # For PDF files, extract text using PyMuPDF
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                text = pdf_processor.extract_text_from_pdf(tmp_path)
            finally:
                os.unlink(tmp_path)
            
            if not text.strip():
                raise HTTPException(
                    status_code=422,
                    detail="Could not extract text from PDF. The file may be scanned/image-only. "
                           "Please use a text-based PDF or convert to TXT first."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
        
        # Extract entities using selected model
        if model == "baseline":
            entities = baseline_model.extract_entities(text)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model}' not yet implemented. Use 'baseline'."
            )
        
        # Validate entities
        validation_results = entity_validator.validate_all(entities)
        
        # Extract and validate dates
        date_entities = date_validator.extract_date_entities(entities)
        
        # Standardize dates
        dates_info = {}
        for key, date_str in date_entities.items():
            if date_str and key != 'other_dates':
                iso_date = date_validator.standardize_date(date_str)
                dates_info[key] = DateInfo(
                    text=date_str,
                    iso=iso_date,
                    confidence=0.9
                )
        
        # Check date consistency
        date_consistency = date_validator.validate_date_consistency(
            effective_date=date_entities.get('effective_date'),
            termination_date=date_entities.get('termination_date'),
            expiration_date=date_entities.get('expiration_date')
        )
        
        # Determine validation status
        if not validation_results['overall_valid'] or not date_consistency['valid']:
            validation_status = "FAILED"
        elif validation_results['total_warnings'] > 0:
            validation_status = "WARNING"
        else:
            validation_status = "PASSED"
        
        # Collect all errors and warnings
        all_errors = date_consistency.get('errors', [])
        all_warnings = []
        
        for key, val_result in validation_results.items():
            if isinstance(val_result, dict):
                all_errors.extend(val_result.get('errors', []))
                all_warnings.extend(val_result.get('warnings', []))
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            label = entity['label']
            if label not in entities_by_type:
                entities_by_type[label] = []
            
            entities_by_type[label].append(EntityResponse(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity.get('confidence', 1.0),
                method=entity.get('method', 'unknown')
            ))
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Build response
        response = ExtractionResponse(
            document_id=file.filename,
            entities=entities_by_type,
            dates=dates_info if dates_info else None,
            validation_status=validation_status,
            validation_errors=all_errors,
            validation_warnings=all_warnings,
            processing_time_ms=processing_time,
            model_used=model
        )
        
        logger.info(f"Processed {file.filename} in {processing_time:.2f}ms "
                   f"({len(entities)} entities extracted)")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the API server
    
    Args:
        host: Host address
        port: Port number
        reload: Enable auto-reload
    """
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server(reload=True)
