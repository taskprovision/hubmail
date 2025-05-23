from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EmailClassification(str, Enum):
    URGENT = "URGENT"
    BUSINESS = "BUSINESS"
    PERSONAL = "PERSONAL"
    SPAM = "SPAM"
    UNKNOWN = "UNKNOWN"

class Email(BaseModel):
    """Email model representing an email message"""
    id: str
    from_address: EmailStr = Field(..., alias="from")
    to_address: Optional[str] = Field(None, alias="to")
    subject: str
    body: str
    html: Optional[str] = None
    date: datetime
    has_attachments: bool = False
    attachments: List[Dict[str, Any]] = []
    
    class Config:
        allow_population_by_field_name = True
        
    def dict(self, *args, **kwargs):
        """Override dict method to handle the 'from' field correctly"""
        d = super().dict(*args, **kwargs)
        if "from_address" in d and kwargs.get("by_alias", False) is False:
            d["from"] = d.pop("from_address")
        if "to_address" in d and kwargs.get("by_alias", False) is False:
            d["to"] = d.pop("to_address")
        return d

class EmailAnalysis(BaseModel):
    """Model representing the analysis of an email"""
    classification: EmailClassification
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    suggested_action: str
    
    def is_urgent(self) -> bool:
        """Check if the email is classified as urgent"""
        return self.classification == EmailClassification.URGENT
    
    def is_spam(self) -> bool:
        """Check if the email is classified as spam"""
        return self.classification == EmailClassification.SPAM
    
    def meets_threshold(self, threshold: float) -> bool:
        """Check if the confidence meets a certain threshold"""
        return self.confidence >= threshold
