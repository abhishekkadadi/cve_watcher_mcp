from contextlib import AsyncExitStack
from agents import Agent, Tool, Runner, OpenAIChatCompletionsModel, trace
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import json
from agents.mcp import MCPServerStdio
import asyncio
from IPython.display import Markdown, display

from templates import (
    researcher_instructions
)
from mcp_params import researcher_mcp_server_params
load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MAX_TURNS = 30

gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
mcp_servers = [MCPServerStdio(params, client_session_timeout_seconds=300) for params in researcher_mcp_server_params()]

def get_model(model_name: str):
    if "gemini" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=gemini_client)
    else:
        return model_name



async def get_researcher(mcp_servers) -> Agent:
    instructions = researcher_instructions()

    researcher = Agent(
        name="Researcher",
        instructions=instructions,
        model=get_model("gemini-2.5-flash"),
        mcp_servers=mcp_servers,
    )

    return researcher



async def run_function():
    research_question = "New CVEs, Supply chain attacks and vulnerabilities today"
    for server in mcp_servers:
        await server.connect()
    researcher = await get_researcher(mcp_servers)
    print(researcher)
    with trace("Researcher"):
        result = await Runner.run(researcher, research_question, max_turns=2)
    return result

if __name__ == "__main__":
    print(f"Starting scheduler to run every  minutes")
    result = asyncio.run(run_function())
    print(result)