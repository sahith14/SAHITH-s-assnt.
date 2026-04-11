"""
Friday Unified Server – FastAPI for frontend + MCP tools
Run with: python server.py
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os
import asyncio

# Import MCP components
from friday.tools import register_all_tools
from friday.prompts import register as register_all_prompts
from friday.resources import register_all_resources
from friday.config import config

# Create FastAPI app
app = FastAPI(title="Friday Assistant API")

# CORS – allows frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq (FREE - get key from https://console.groq.com/keys)
GROQ_API_KEY = os.getenv("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")
if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not found in .env file")
    print("💡 Get your free key from: https://console.groq.com/keys")
    
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Import tools from your actual files
from friday.tools.web import get_world_news, search_web, fetch_url, open_world_monitor
from friday.tools.system import get_current_time, get_system_info
from friday.tools.utils import format_json, word_count

# System prompt for Friday
SYSTEM_PROMPT = """You are F.R.I.D.A.Y. — Fully Responsive Intelligent Digital Assistant.
You are calm, composed, and always informed. Speak like a trusted aide.

Available tools (call them when appropriate):
- get_world_news: Get latest global headlines
- open_world_monitor: Open visual world dashboard
- get_current_time: Get current date/time
- get_system_info: Get system information

Rules:
1. Call tools silently without announcing them
2. Keep responses short (2-4 sentences)
3. Address user as "boss" occasionally
4. No markdown, no lists – you are speaking"""

@app.post("/chat")
async def chat(req: dict):
    user_message = req.get("message", "")
    
    # First, check if user wants news
    if any(word in user_message.lower() for word in ["news", "world", "happening", "brief me", "catch me up"]):
        try:
            news_result = await get_world_news()
            # Call open_world_monitor automatically after news
            await open_world_monitor()
            return {"reply": f"Here's what's happening, boss:\n\n{news_result}\n\nI've opened the world monitor for you."}
        except Exception as e:
            return {"reply": f"News feed is unresponsive, boss. {str(e)}"}
    
    # Check for time request
    if any(word in user_message.lower() for word in ["time", "clock", "what time"]):
        time_result = get_current_time()
        return {"reply": f"The current time is {time_result}, boss."}
    
    # Default: use Groq (FREE)
    if client:
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",  # Free model, very fast
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            return {"reply": reply}
        except Exception as e:
            return {"reply": f"Neural uplink failed, boss. {str(e)}"}
    else:
        return {"reply": "⚠️ Groq API key not configured. Add GROQ_API_KEY to .env file. Get free key from: https://console.groq.com/keys"}

@app.get("/tools")
async def list_tools():
    """Return available MCP tools"""
    return {"tools": ["get_world_news", "open_world_monitor", "get_current_time", "get_system_info", "format_json", "word_count"]}

def main():
    import uvicorn
    print("=" * 50)
    print("🚀 FRIDAY SERVER STARTING (Groq AI)")
    print("=" * 50)
    print("📡 Server: http://localhost:8000")
    print("📡 Endpoints: POST /chat, GET /tools")
    if client:
        print("🤖 AI Mode: ENABLED (Groq - Free & Fast)")
    else:
        print("⚠️ AI Mode: DISABLED (Missing GROQ_API_KEY)")
        print("💡 Get free key: https://console.groq.com/keys")
    print("=" * 50)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
