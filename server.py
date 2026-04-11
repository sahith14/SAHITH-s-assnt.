"""
Friday MCP Server — Entry Point
Run with: python server.py
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from openai import OpenAI
import os
from mcp.server.fastmcp import FastMCP
from friday.tools import register_all_tools
from friday.prompts import register_all_prompts
from friday.resources import register_all_resources
from friday.config import config

# Create the MCP server instance
mcp = FastMCP(
    name=config.SERVER_NAME,
    instructions=(
        "You are Friday, a Tony Stark-style AI assistant. "
        "You have access to a set of tools to help the user. "
        "Be concise, accurate, and a little witty."
    ),
)

app = FastAPI()

# Allow frontend to talk to backend (important or it will silently fail)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/chat")
async def chat(req: dict):
    user_message = req.get("message", "")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=user_message
    )

    return {
        "reply": response.output_text
    }

# Register tools, prompts, and resources
register_all_tools(mcp)
register_all_prompts(mcp)
register_all_resources(mcp)

def main():
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
