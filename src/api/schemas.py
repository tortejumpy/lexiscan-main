"""
Pydantic Schemas for API Request/Response
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class EntityResponse(BaseModel):
    """Single entity in response"""
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type (PARTY, DATE, AMOUNT, etc.)")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(..., description="Confidence score (0-1)")
    method: str = Field(..., description="Extraction method (regex, spacy, bilstm)")


class DateInfo(BaseModel):
    """Date information"""
    text: str = Field(..., description="Original date text")
    iso: Optional[str] = Field(None, description="ISO 8601 formatted date")
    confidence: float = Field(..., description="Confidence score")


class ExtractionResponse(BaseModel):
    """Response for entity extraction"""
    document_id: str = Field(..., description="Document identifier")
    entities: Dict[str, List[EntityResponse]] = Field(..., description="Extracted entities by type")
    dates: Optional[Dict[str, DateInfo]] = Field(None, description="Categorized dates")
    validation_status: str = Field(..., description="Validation status (PASSED/FAILED/WARNING)")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="NER model used")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: Dict[str, bool] = Field(..., description="Model loading status")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
