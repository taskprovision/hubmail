from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import os
import json
import datetime
import uvicorn
from dotenv import load_dotenv

# Import our modules
from ..utils.logger import get_logger
from ..models.email import Email, EmailAnalysis
from ..flows.email_processor import process_email, check_emails
from ..flows.llm_service import analyze_email_content

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HubMail API",
    description="Email automation system with LLM processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for API requests and responses
class EmailRequest(BaseModel):
    from_address: EmailStr
    subject: str
    body: str
    
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    
class EmailAnalysisResponse(BaseModel):
    email: Dict[str, Any]
    analysis: Dict[str, Any]

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }

# Test email analysis endpoint
@app.post("/api/test-analysis", response_model=EmailAnalysisResponse)
async def test_analysis(email_request: EmailRequest):
    try:
        # Create email object
        email = Email(
            id=f"test-{datetime.datetime.now().timestamp()}",
            from_address=email_request.from_address,
            subject=email_request.subject,
            body=email_request.body,
            date=datetime.datetime.now()
        )
        
        # Analyze with LLM
        analysis = await analyze_email_content(email)
        
        return {
            "email": email.dict(),
            "analysis": analysis.dict()
        }
    except Exception as e:
        logger.error(f"Error in test analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Trigger email check
@app.post("/api/check-emails")
async def trigger_email_check(background_tasks: BackgroundTasks):
    try:
        # Run email check in background
        background_tasks.add_task(check_emails)
        
        return {
            "status": "processing",
            "message": "Email check triggered successfully"
        }
    except Exception as e:
        logger.error(f"Error triggering email check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get recent email analyses
@app.get("/api/emails")
async def get_recent_emails(limit: int = 10):
    try:
        # This would be implemented to fetch from storage
        # For now, return a placeholder
        return {
            "emails": []
        }
    except Exception as e:
        logger.error(f"Error getting recent emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Start the server if run directly
if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=int(os.getenv("API_PORT", 3001)), reload=True)
