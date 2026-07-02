# ruff: noqa
import datetime
import re
import json
import os
import sys
from typing import AsyncGenerator, Dict, Any, List
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.workflow import Workflow, START, node, FunctionNode, Event
from google.adk.agents.context import Context
from google.adk.events.request_input import RequestInput
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.config import config

# ----------------------------------------------------------------------
# 1. Models & MCP Server Setup
# ----------------------------------------------------------------------

llm_model = Gemini(
    model=config.model,
    retry_options=types.HttpRetryOptions(attempts=3)
)

# Resolve path to the MCP server script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER_PATH = os.path.join(CURRENT_DIR, "mcp_server.py")

# Create standard stdio connection parameters to run our server script
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER_PATH],
    )
)

# ----------------------------------------------------------------------
# 2. Sub-Agents Definition
# ----------------------------------------------------------------------

# Developmental Coach Agent
developmental_coach = LlmAgent(
    name="developmental_coach",
    model=llm_model,
    description="Provides age-appropriate parenting advice, kids screen-time balances, and moral disciplining strategies.",
    instruction=(
        "You are the Developmental Coach. You specialize in giving age-appropriate parenting tips, "
        "screen-time limits, and moral disciplining/guidance. "
        "Analyze the query and provide actionable, age-appropriate strategies. Focus on positive reinforcement "
        "and age-appropriate behavior expectations. Use recommend_screen_time_limit for screen-time and "
        "suggest_discipline_strategy for discipline advice."
    ),
    tools=[
        McpToolset(
            connection_params=mcp_connection,
            tool_filter=["recommend_screen_time_limit", "suggest_discipline_strategy"]
        )
    ]
)

# Kids Mental Health Advocate Agent
mental_health_advocate = LlmAgent(
    name="mental_health_advocate",
    model=llm_model,
    description="Provides kids emotional support, mental health advice, mindfulness, and coping techniques.",
    instruction=(
        "You are the Mental Health Advocate. You focus on children's emotional well-being, stress, anxiety, "
        "and mental health support. Suggest mindfulness or emotional regulation activities. "
        "ALWAYS include a brief disclaimer that you are an AI parenting assistant, not a licensed therapist. "
        "Use fetch_mental_health_activities to suggest appropriate mindfulness/calming activities."
    ),
    tools=[
        McpToolset(
            connection_params=mcp_connection,
            tool_filter=["fetch_mental_health_activities"]
        )
    ]
)

# Disability & Neurodiversity Support Agent
disability_support_agent = LlmAgent(
    name="disability_support_agent",
    model=llm_model,
    description="Provides resources, school IEP guidance, and support for children with physical/cognitive disabilities or neurodivergence (ADHD, Autism).",
    instruction=(
        "You are the Disability Support Agent. You specialize in supporting parents of neurodivergent children (ADHD, Autism, etc.) "
        "or children with physical or cognitive disabilities. Provide guidance on special education accommodations, "
        "Individualized Education Programs (IEPs), and adaptive strategies. Recommend helpful organizations or resource types. "
        "Use get_disability_resources to fetch helpful organizations and accommodations guidelines."
    ),
    tools=[
        McpToolset(
            connection_params=mcp_connection,
            tool_filter=["get_disability_resources"]
        )
    ]
)

# Orchestrator Agent (with delegation tools)
orchestrator_agent = LlmAgent(
    name="orchestrator_agent",
    model=llm_model,
    instruction=(
        "You are the Parent Pilot Orchestrator. Your role is to coordinate parenting advice for the user query. "
        "You have access to three specialized sub-agents via their respective Agent Tools:\n"
        "1. developmental_coach: Use for developmental age-appropriate tips, screen time, and moral disciplining.\n"
        "2. mental_health_advocate: Use for children's emotional well-being, stress, and anxiety.\n"
        "3. disability_support_agent: Use for special needs, IEPs, neurodivergence (ADHD, Autism), or other disabilities.\n\n"
        "Select the most appropriate sub-agent to delegate the query. Once you get their response, summarize it for the user. "
        "If the response details a screen time calculation or a moral discipline plan, announce that this recommendation "
        "requires parent confirmation before final approval."
    ),
    tools=[
        AgentTool(developmental_coach),
        AgentTool(mental_health_advocate),
        AgentTool(disability_support_agent)
    ]
)

# ----------------------------------------------------------------------
# 2. Workflow Nodes
# ----------------------------------------------------------------------

def security_checkpoint(ctx: Context, node_input: types.Content) -> Event:
    """Scrubs PII (phone/email), checks for prompt injection, and audits queries."""
    query_text = ""
    if hasattr(node_input, 'parts') and node_input.parts:
        query_text = " ".join([p.text for p in node_input.parts if hasattr(p, 'text') and p.text])
    elif isinstance(node_input, str):
        query_text = node_input
    
    ctx.state["query"] = query_text
    
    # PII Scrubbing
    scrubbed_text = query_text
    pii_redacted = False
    if config.pii_redaction_enabled:
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        
        if re.search(email_pattern, scrubbed_text):
            scrubbed_text = re.sub(email_pattern, "[EMAIL_REDACTED]", scrubbed_text)
            pii_redacted = True
        if re.search(phone_pattern, scrubbed_text):
            scrubbed_text = re.sub(phone_pattern, "[PHONE_REDACTED]", scrubbed_text)
            pii_redacted = True
            
    ctx.state["scrubbed_query"] = scrubbed_text
    ctx.state["pii_redacted"] = pii_redacted
    
    # Prompt Injection / Abuse Detection
    injection_detected = False
    injection_keywords = ["ignore instructions", "jailbreak", "system prompt", "dan mode", "physical discipline", "beat child", "hit child"]
    for kw in injection_keywords:
        if kw in query_text.lower():
            injection_detected = True
            break
            
    # Domain Rule check
    medical_alert = False
    medical_keywords = ["diagnose", "prescribe", "medication dose", "cure sickness", "disease cure"]
    for kw in medical_keywords:
        if kw in query_text.lower():
            medical_alert = True
            break
            
    # Write to audit log
    audit_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pii_redacted": pii_redacted,
        "injection_detected": injection_detected,
        "medical_alert": medical_alert,
        "severity": "CRITICAL" if (injection_detected or pii_redacted) else "INFO"
    }
    if "audit_log" not in ctx.state:
        ctx.state["audit_log"] = []
    ctx.state["audit_log"].append(audit_entry)
    
    # Print JSON audit log
    print(f"[AUDIT LOG] {json.dumps(audit_entry)}")
    
    if injection_detected:
        ctx.state["security_violation"] = True
        return Event(
            output={"status": "rejected", "reason": "Security violation detected."},
            route="security_event"
        )
        
    return Event(
        output=scrubbed_text,
        route="clear"
    )


def security_event_handler(ctx: Context, node_input: dict) -> Event:
    """Handles blocked requests due to security flags."""
    msg = "⚠️ SECURITY ACTION TAKEN: The system detected sensitive or inappropriate content and blocked this request. Please review our safety guidelines."
    return Event(
        content=types.Content(role='model', parts=[types.Part.from_text(text=msg)]),
        output={"response": msg}
    )


async def human_approval_gate(ctx: Context, node_input: types.Content) -> AsyncGenerator[Event, None]:
    """Pauses for human confirmation on screen time recommendations or disciplining plans."""
    text_response = ""
    if hasattr(node_input, 'parts') and node_input.parts:
        text_response = "".join([p.text for p in node_input.parts if hasattr(p, 'text') and p.text])
    elif isinstance(node_input, str):
        text_response = node_input
    elif isinstance(node_input, dict) and "response" in node_input:
        text_response = node_input["response"]
        
    ctx.state["response"] = text_response
    
    # Check if this requires parent approval
    needs_approval = "screen time" in text_response.lower() or "discipline" in text_response.lower()
    ctx.state["needs_approval"] = needs_approval
    
    if needs_approval:
        if not ctx.resume_inputs:
            yield RequestInput(
                interrupt_id="parent_confirm",
                message="📋 PARENTAL GATEWAY: These guidelines involve scheduling or disciplining rules. Do you approve implementing these tips? (Type 'approve' to continue)"
            )
            return
        
        reply = ctx.resume_inputs.get("parent_confirm", "").strip().lower()
        ctx.state["approval_status"] = reply
        
        if "approve" in reply or "yes" in reply:
            msg = f"✅ Approved by Parent. Implementing parenting recommendations:\n\n{text_response}"
        else:
            msg = "❌ Parenting recommendations denied by parent. Let's adjust the settings. What would you like to change?"
        
        yield Event(
            content=types.Content(role='model', parts=[types.Part.from_text(text=msg)]),
            output={"response": msg}
        )
        return
        
    # Standard pass-through
    yield Event(
        content=types.Content(role='model', parts=[types.Part.from_text(text=text_response)]),
        output={"response": text_response}
    )


def final_output_node(ctx: Context, node_input: dict) -> dict:
    """Terminal node returning the processed response."""
    return node_input

# ----------------------------------------------------------------------
# 3. Workflow Graph Configuration
# ----------------------------------------------------------------------

app_workflow = Workflow(
    name="parent_pilot_workflow",
    edges=[
        ('START', security_checkpoint),
        (security_checkpoint, orchestrator_agent, "clear"),
        (security_checkpoint, security_event_handler, "security_event"),
        (orchestrator_agent, human_approval_gate),
        (human_approval_gate, final_output_node),
        (security_event_handler, final_output_node)
    ]
)

app = App(
    root_agent=app_workflow,
    name="app",
)
