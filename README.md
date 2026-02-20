# Reddit Mastermind - Content Calendar Generator

An automated system for generating Reddit content calendars that drive engagement and inbound leads.

## Features

- **Automated Content Generation**: Creates natural, engaging Reddit posts and replies
- **Multi-Persona Support**: Manages multiple personas with distinct voices
- **Smart Distribution**: Prevents overposting and ensures natural conversation flow
- **Quality Validation**: Checks for edge cases and ensures high-quality output
- **Weekly Calendar Generation**: Produces structured content calendars

## Quick Setup

### 1. Get Google Gemini API Key (100% Free!)

- Go to https://makersuite.google.com/app/apikey
- Sign in with Google account (no payment method needed!)
- Create API key (starts with `AIza...`)
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR: venv\Scripts\activate.bat  # Windows CMD

# Install packages
pip install -r requirements.txt
```

### 3. Configure API Key

Create `.env` file in project root:

```
GOOGLE_API_KEY=AIza-your-actual-key-here
```

### 4. Run Application

```bash
uvicorn main:app --reload
```

### 5. Open Browser

Go to: **http://localhost:8000**

**For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## Quick Start

1. Click "Load Sample Data (SlideForge)" to populate the form with example data
2. Review the inputs (you can modify them)
3. Click "Generate Calendar" to create your content calendar
4. Review the quality score and warnings
5. Use "Generate Next Week" to create subsequent weeks
6. Export the calendar as JSON if needed

## Features

- **Natural Content Generation**: Uses GPT-4 to create authentic Reddit posts and replies
- **Smart Scheduling**: Distributes posts across the week with natural timing
- **Quality Validation**: Checks for overposting, topic overlap, and conversation flow
- **Multi-Persona Support**: Manages multiple personas with distinct voices
- **Subreddit Distribution**: Prevents spamming the same subreddit
- **Export Functionality**: Export calendars as JSON for integration

## Usage

1. Enter company information
2. Add personas (2+)
3. Specify subreddits
4. Add ChatGPT queries to target
5. Set number of posts per week
6. Generate calendar
7. Click "Generate Next Week" for subsequent weeks

## Project Structure

```
.
├── main.py                 # FastAPI application
├── models.py               # Data models
├── content_generator.py    # Content generation logic
├── scheduler.py            # Scheduling and distribution
├── validator.py            # Quality validation
├── calendar_generator.py   # Main calendar generation orchestrator
├── static/                 # Frontend assets
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/                   # Sample data and storage
└── requirements.txt
```
