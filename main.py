"""
FastAPI application for Reddit Mastermind content calendar generator.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import json
import os

from models import CalendarRequest, CalendarResponse, CompanyInfo, Persona, Keyword
import json
import os
from dotenv import load_dotenv

# Load environment variables before importing CalendarGenerator
load_dotenv(override=True)

from calendar_generator import CalendarGenerator

app = FastAPI(title="Reddit Mastermind", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize generator
generator = CalendarGenerator()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>Reddit Mastermind</title></head>
            <body>
                <h1>Reddit Mastermind</h1>
                <p>Please ensure static/index.html exists</p>
            </body>
        </html>
        """

@app.post("/api/generate-calendar", response_model=CalendarResponse)
async def generate_calendar(request: CalendarRequest):
    """
    Generate a content calendar based on the request.
    
    Args:
        request: CalendarRequest with company info, personas, etc.
        
    Returns:
        CalendarResponse with generated calendar
    """
    try:
        print(f"\n{'='*80}")
        print(f"📥 RECEIVED CALENDAR GENERATION REQUEST")
        print(f"  Company: {request.company_info.name}")
        print(f"  Personas: {len(request.personas)}")
        print(f"  Subreddits: {len(request.subreddits)}")
        print(f"  Keywords: {len(request.keywords)}")
        print(f"  Posts per week: {request.posts_per_week}")
        print(f"{'='*80}\n")
        
        response = generator.generate_calendar(request)
        
        print(f"\n{'='*80}")
        print(f"✅ CALENDAR GENERATED SUCCESSFULLY")
        print(f"  Total entries: {len(response.calendar.entries)}")
        print(f"  Quality score: {response.quality_score}/10")
        print(f"{'='*80}\n")
        
        return response
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        # Log full error to server console
        print(f"\n{'='*80}")
        print(f"❌ ERROR GENERATING CALENDAR")
        print(f"  Error: {error_msg}")
        print(f"  Full traceback:")
        print(f"{error_traceback}")
        print(f"{'='*80}\n")
        
        # Provide more helpful error message to client
        if "GROQ_API_KEY" in error_msg or "Groq API" in error_msg:
            detail_msg = f"Groq API Error: {error_msg}. Please check your GROQ_API_KEY in .env file. Get a free key at https://console.groq.com/"
        else:
            detail_msg = f"Calendar Generation Failed: {error_msg}"
        
        raise HTTPException(status_code=500, detail=detail_msg)

@app.post("/api/generate-next-week")
async def generate_next_week(data: dict):
    """
    Generate calendar for the next week.
    
    Args:
        data: Dict with 'request' (CalendarRequest) and 'current_week_start' (ISO string)
        
    Returns:
        CalendarResponse for next week
    """
    try:
        request = CalendarRequest(**data["request"])
        week_start_str = data["current_week_start"]
        week_start = datetime.fromisoformat(week_start_str.replace("Z", "+00:00"))
        response = generator.generate_next_week(request, week_start)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-data")
async def get_sample_data():
    """Return sample data for testing."""
    # Load from JSON file
    sample_data_path = os.path.join("data", "sample_company.json")
    try:
        with open(sample_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Convert to Pydantic models
        company_info = CompanyInfo(**data["company_info"])
        personas = [Persona(**p) for p in data["personas"]]
        keywords = [Keyword(**k) for k in data["keywords"]]
        
        return {
            "company_info": company_info.dict(),
            "personas": [p.dict() for p in personas],
            "subreddits": data["subreddits"],
            "keywords": [k.dict() for k in keywords],
            "posts_per_week": data["posts_per_week"]
        }
    except FileNotFoundError:
        # Fallback to hardcoded data
        sample_company = CompanyInfo(
            name="Slideforge",
            website="slideforge.ai",
            description="AI-powered presentation tool",
            target_audience=["operators", "consultants", "founders"],
            key_features=["AI-powered", "Templates", "API"],
            domain="presentation tools"
        )
        
        sample_personas = [
            Persona(
                name="Riley Hart",
                username="riley_ops",
                role="Head of Operations",
                voice="Precise, organized",
                interests=["operations", "process design"],
                posting_style="Thoughtful, shares experiences"
            )
        ]
        
        sample_keywords = [
            Keyword(keyword_id="K1", keyword="best ai presentation maker")
        ]
        
        return {
            "company_info": sample_company.dict(),
            "personas": [p.dict() for p in sample_personas],
            "subreddits": ["PowerPoint", "startups"],
            "keywords": [k.dict() for k in sample_keywords],
            "posts_per_week": 3
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

