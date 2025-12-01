import os
from typing import Any, Dict
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Try to import ADK components, but don't fail if they're not available
try:
    from google.adk.agents import Agent, LlmAgent
    from google.adk.apps.app import App, EventsCompactionConfig
    from google.adk.models.google_llm import Gemini
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.adk.tools.tool_context import ToolContext
    from google.genai import types
    from google.adk.tools import google_search
    ADK_AVAILABLE = True
except Exception as e:
    print(f"Warning: ADK components not available: {e}")
    ADK_AVAILABLE = False

# =====================================================================================
# CONFIG
# =====================================================================================

APP_NAME = "default"
USER_ID = "default"
MODEL_NAME = "gemini-2.5-flash-lite"

# =====================================================================================
# AGENTS DEFINITIONS (Optional - only if ADK is available)
# =====================================================================================

if ADK_AVAILABLE:
    def get_motivation(tool_context: ToolContext) -> dict:
        """
        Fetch a random motivational quote from the motivational API.
        Returns:
            A dict with status and quote.
        """
        try:
            response = httpx.get("https://motivational-api.vercel.app/motivational")
            response.raise_for_status()
            data = response.json()
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

If the user asks for motivation, mental support, or "quote," you should call the tool `get_motivation` to fetch a motivational quote, then send it.

Otherwise, think step-by-step internally for coding problems but only output the final clean solution.

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

    def store_message(tool_context: ToolContext, role: str, content: str):
        history = tool_context.state.get("chat_history", [])
        history.append({"role": role, "content": content})
        tool_context.state["chat_history"] = history
        return {"status": "saved"}

    def get_history(tool_context: ToolContext):
        return {"history": tool_context.state.get("chat_history", [])}

    # Setup ADK agents
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

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service, app_name="default")
    print("✓ ADK agents initialized successfully")
else:
    print("⚠ ADK not available - using basic Gemini API only")

# =====================================================================================
# FASTAPI APP
# =====================================================================================

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    user_id: str

@app.get("/", response_class=HTMLResponse)
async def root():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "index.html")
    with open(index_path) as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/chat")
async def chat(request: ChatRequest):
    # Use the Gemini model directly via google-genai
    print(f"[CHAT] Received request: prompt='{request.prompt}', user_id='{request.user_id}'")
    try:
        from google.genai import Client
        print("[CHAT] Imported Client")
        
        # Create the client with API key
        api_key = os.getenv("GOOGLE_API_KEY")
        print(f"[CHAT] API Key set: {bool(api_key)}")
        client = Client(api_key=api_key)
        print("[CHAT] Client created")
        
        # Enhanced system instruction for better responses
        system_instruction = """You are a helpful learning assistant. When responding:
1. Start with a concise, actionable insight or answer (max 2-3 sentences)
2. If providing steps, use numbered lists with bullet points
3. End with a brief motivational note
4. Keep language simple and encouraging
5. Format with clear sections using ** for emphasis
6. Make content scannable and easy to read"""
        
        # Generate content with enhanced system instruction
        print(f"[CHAT] Calling generate_content with model={MODEL_NAME}")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_instruction}]
                },
                {
                    "role": "user", 
                    "parts": [{"text": request.prompt}]
                }
            ]
        )
        print(f"[CHAT] Got response: {type(response)}")
        
        text_response = response.text
        print(f"[CHAT] Text extracted: {text_response[:50]}...")
        
        # Format the response for better readability
        formatted_response = format_agent_response(text_response)
        
        return {"response": formatted_response}
    except Exception as e:
        import traceback
        print(f"[CHAT] Error occurred: {e}")
        traceback.print_exc()
        return {"response": f"Error: {str(e)}", "error": True}


def format_agent_response(text: str) -> str:
    """Format agent response for better readability - condensed paragraph format"""
    # Clean up the text
    text = text.strip()
    
    # Remove markdown formatting
    text = text.replace('**', '')  # Remove bold markdown
    text = text.replace('##', '')  # Remove headers
    text = text.replace('*', '')   # Remove italic/bold asterisks
    
    # Convert multi-line lists into single paragraph format
    lines = text.split('\n')
    sections = []
    current_section = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            # Empty line - marks section break
            if current_section:
                sections.append(' '.join(current_section))
                current_section = []
        else:
            # Remove numbering and bullets, keep content
            cleaned = stripped
            if cleaned[0].isdigit() and '.' in cleaned[:3]:
                # Remove number prefix (1. becomes content)
                cleaned = cleaned.split('.', 1)[1].strip() if '.' in cleaned else cleaned
            elif cleaned.startswith('•') or cleaned.startswith('-'):
                # Remove bullet
                cleaned = cleaned[1:].strip()
            
            current_section.append(cleaned)
    
    # Add remaining section
    if current_section:
        sections.append(' '.join(current_section))
    
    # Join sections with " | " separator for visual breaks
    result = ' | '.join(sections)
    
    # Clean up multiple spaces
    result = ' '.join(result.split())
    
    return result

if __name__ == "__main__":
    try:
        print("Starting Uvicorn server on http://localhost:8001...")
        print(f"API Key: {os.getenv('GOOGLE_API_KEY')[:20] if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}...")
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
    except KeyboardInterrupt:
        print("Server interrupted")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
