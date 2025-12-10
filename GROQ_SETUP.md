# Groq API Setup Guide

## 🚀 Get Your Free Groq API Key

### Step 1: Create Groq Account
1. Go to: **https://console.groq.com/**
2. Click **"Sign Up"** or **"Get Started"**
3. Enter your email and create password
4. Verify your email address

### Step 2: Get API Key
1. Once logged in, navigate to **"API Keys"** section
2. Click **"Create API Key"**
3. Give it a name (e.g., "Reddit Mastermind")
4. **Copy the API key immediately!** (shown only once)

### Step 3: Update Your Project
1. Open `.env` file in project root
2. Add or update:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
3. Save the file

### Step 4: Install Dependencies
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 5: Restart Server
The server should auto-reload, or restart it manually.

## ✅ Benefits of Groq

- **FREE**: Generous free tier with no credit card required
- **Fast**: Ultra-fast inference with low latency
- **OpenAI-Compatible**: Uses standard OpenAI Python library
- **No Credits Needed**: Unlike Grok/xAI, Groq is free to use
- **High Rate Limits**: Very generous rate limits for free tier

## 📊 Available Models

- `llama-3.1-70b-versatile` - Best for general use (default)
- `mixtral-8x7b-32768` - Good for longer context
- `llama-3.1-8b-instant` - Faster, smaller model
- `gemma-7b-it` - Google's Gemma model

## 💰 Pricing

- **FREE TIER**: Very generous limits, no payment required
- **Paid Tier**: Available if you need higher limits

## 🎯 That's It!

Your system is now using Groq API. Generate a calendar and you should see real AI-generated content!

## 🔧 Troubleshooting

### Error: "GROQ_API_KEY not found"
- Make sure your `.env` file has `GROQ_API_KEY=your_key_here`
- Restart the server after updating `.env`

### Error: "401 Unauthorized"
- Check that your API key is correct
- Make sure there are no extra spaces in the `.env` file

### Error: "429 Rate Limit"
- Groq has generous free limits, but if you hit them, wait a moment and try again
- Free tier typically allows thousands of requests per minute

