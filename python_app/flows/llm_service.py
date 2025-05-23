from prefect import task
import aiohttp
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from ..models.email import Email, EmailAnalysis, EmailClassification
from ..utils.logger import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_CONTAINER_PORT", "11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
LLM_MODEL = os.getenv("LLM_MODEL", "llama2:7b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))

@task(name="Analyze Email Content", retries=2, retry_delay_seconds=5)
async def analyze_email_content(email: Email) -> EmailAnalysis:
    """
    Analyze email content using LLM
    
    Args:
        email: The email to analyze
        
    Returns:
        EmailAnalysis object with classification results
    """
    logger.info(f"Analyzing email: {email.id}")
    
    try:
        # Create prompt for LLM
        prompt = create_prompt(email)
        
        # Call LLM API
        response = await call_llm_api(prompt)
        
        # Parse response
        analysis = parse_llm_response(response)
        
        logger.info(f"Email {email.id} classified as {analysis.classification} with confidence {analysis.confidence}")
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing email {email.id}: {str(e)}")
        # Return default analysis in case of error
        return EmailAnalysis(
            classification=EmailClassification.BUSINESS,
            confidence=0.5,
            reasoning="Error in analysis, defaulting to business classification",
            suggested_action="Review manually due to analysis error"
        )

def create_prompt(email: Email) -> str:
    """
    Create a prompt for the LLM
    
    Args:
        email: The email to analyze
        
    Returns:
        Formatted prompt string
    """
    # Truncate body if too long
    body = email.body[:1000] + ("..." if len(email.body) > 1000 else "")
    
    return f"""Analyze this email and classify it:

From: {email.from_address}
Subject: {email.subject}
Body: {body}

Classify as one of: URGENT, BUSINESS, SPAM, PERSONAL
Provide reasoning and confidence score.

Respond in JSON format:
{{
  "classification": "URGENT|BUSINESS|SPAM|PERSONAL",
  "confidence": 0.95,
  "reasoning": "explanation",
  "suggested_action": "action to take"
}}"""

async def call_llm_api(prompt: str) -> str:
    """
    Call the LLM API
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        Raw response from the LLM
    """
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": LLM_MODEL,
                "prompt": prompt,
                "temperature": LLM_TEMPERATURE,
                "max_tokens": LLM_MAX_TOKENS,
                "stream": False
            }
            
            async with session.post(OLLAMA_URL, json=payload, timeout=30) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM API error: {response.status} - {error_text}")
                
                data = await response.json()
                return data.get("response", "")
    except Exception as e:
        logger.error(f"Error calling LLM API: {str(e)}")
        raise

def parse_llm_response(response: str) -> EmailAnalysis:
    """
    Parse the LLM response
    
    Args:
        response: Raw response from the LLM
        
    Returns:
        EmailAnalysis object
    """
    try:
        # Try to extract JSON from the response
        json_match = None
        for line in response.split("\n"):
            if line.strip().startswith("{") and line.strip().endswith("}"):
                json_match = line.strip()
                break
        
        if not json_match:
            # Try to find JSON using regex-like approach
            start_idx = response.find("{")
            end_idx = response.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_match = response[start_idx:end_idx+1]
        
        if json_match:
            data = json.loads(json_match)
            
            # Validate classification
            classification = data.get("classification", "BUSINESS").upper()
            if classification not in [e.value for e in EmailClassification]:
                classification = "BUSINESS"
                
            return EmailAnalysis(
                classification=classification,
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("reasoning", "No reasoning provided"),
                suggested_action=data.get("suggested_action", "No action suggested")
            )
        
        # Fallback parsing if JSON extraction fails
        return fallback_parsing(response)
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return fallback_parsing(response)

def fallback_parsing(response: str) -> EmailAnalysis:
    """
    Fallback parsing when JSON extraction fails
    
    Args:
        response: Raw LLM response
        
    Returns:
        EmailAnalysis object
    """
    # Simple heuristic-based classification
    response_lower = response.lower()
    
    classification = EmailClassification.BUSINESS  # Default
    confidence = 0.5
    
    if any(word in response_lower for word in ["urgent", "emergency", "critical", "important"]):
        classification = EmailClassification.URGENT
        confidence = 0.7
    elif any(word in response_lower for word in ["spam", "scam", "phishing", "advertisement"]):
        classification = EmailClassification.SPAM
        confidence = 0.7
    elif any(word in response_lower for word in ["personal", "private", "family", "friend"]):
        classification = EmailClassification.PERSONAL
        confidence = 0.6
    
    return EmailAnalysis(
        classification=classification,
        confidence=confidence,
        reasoning="Fallback classification due to parsing error",
        suggested_action="Review manually due to parsing error"
    )
