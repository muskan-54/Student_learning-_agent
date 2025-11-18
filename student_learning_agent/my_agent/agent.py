import os
from typing import Any, Dict
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.adk.tools import google_search
import httpx
from google.adk.tools.tool_context import ToolContext

# =====================================================================================
# CONFIG
# =====================================================================================

APP_NAME = "default"
USER_ID = "default"
MODEL_NAME = "gemini-2.5-flash-lite"

# =====================================================================================
# AGENTS DEFINITIONS
# =====================================================================================


def get_motivation(tool_context: ToolContext) -> dict:
    """
    Fetch a random motivational quote from the motivational API.
    Returns:
        A dict with status and quote.
    """
    try:
        response = httpx.get("https://motivational-api.vercel.app/motivational")
        response.raise_for_status()
        data = response.json()  # e.g. {"quote": "...", "author": "..."} or maybe just text
    except Exception as e:
        return {"status": "error", "message": f"Could not fetch quote: {e}"}

    tool_context.state["last_motivation"] = data

    return {"status": "success", "quote": data}


def create_tutor_agent():
    return Agent(
        name="tutor_agent",
        model="gemini-2.0-flash",
        instructions="""
You are a friendly and adaptive Tutor Agent.

Your job is to:
• Explain concepts in simple, beginner-friendly language  
• Detect knowledge gaps and fill them  
• Ask clarifying questions before giving large explanations  
• Use small examples, analogies, and visual-style breakdowns  
• Create personalized learning steps  
• Encourage progress and learning consistency  

Always keep answers short, simple, and supportive.
"""
    )

def planner():
    return Agent(
        name="planner_agent",
        model="gemini-2.0-flash",
        instructions="""
You are the Task Planner Agent.

Your job is to create clear, achievable, and personalized study plans.

You must:
• Gather missing info before planning  
• Break big goals into small steps  
• Create weekly/daily schedules  
• Add realistic time estimates  
• Suggest study techniques (Pomodoro, active recall, spaced repetition)  
• Adapt plan as user progresses  
• Keep everything simple and actionable  
"""
    )


def code_helper():
    return Agent(
        name="code_agent",
        model="gemini-2.0-flash",
        tools=[google_search],
        instructions="""
You are a Code Helper Agent.

If the user asks for motivation, mental support, or “quote,” you should call the tool `get_motivation` to fetch a motivational quote, then send it.

Otherwise, think step-by-step internally for coding problems but only output the final clean solution.
...

Your goals:
• Give short, clear explanations  
• Fix errors & debug quickly  
• Provide production-ready solutions  
• Keep code clean and minimal  
• Encourage the user and guide them  

Rules:
• Do not reveal chain-of-thought  
• Keep answers simple  
"""
    )


# =====================================================================================
# IMPROVED MEMORY — FULL CONVERSATION HISTORY STORAGE
# =====================================================================================

# FIX: This makes agent remember every user–assistant message.
def store_message(tool_context: ToolContext, role: str, content: str):
    history = tool_context.state.get("chat_history", [])
    history.append({"role": role, "content": content})
    tool_context.state["chat_history"] = history
    return {"status": "saved"}


def get_history(tool_context: ToolContext):
    return {"history": tool_context.state.get("chat_history", [])}


# =====================================================================================
# ROOT AGENT
# =====================================================================================

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

root_agent = LlmAgent(
    model=Gemini(
        model=MODEL_NAME,
        retry_options=retry_config,
        system_instruction="""
You are the Main Supervisor Agent.
• Understand user intent
• Save every message to memory using store_message
• Use get_history to maintain context
• Route tasks to tutor_agent, code_agent, planner_agent, or get_motivation
• Keep responses short and friendly.
"""
    ),
    name="main_supervisor",
    description="Main supervisor agent.",
    tools=[
        store_message,
        get_history,
        create_tutor_agent,
        planner,
        code_helper,
        get_motivation
    ]
)

# =====================================================================================
# RUNNER
# =====================================================================================

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, session_service=session_service, app_name="default")

print("✅ Fully upgraded agent with persistent session context is ready!")
