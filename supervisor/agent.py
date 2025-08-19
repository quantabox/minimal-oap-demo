"""
Multi-Agent Supervisor - Configuration-driven supervisor using RemoteGraph
Demonstrates OAP's supervisor pattern with distributed agent communication
"""

import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from langgraph.pregel.remote import RemoteGraph
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from logger import AgentLogger
from config import SystemConfig, AgentEndpoint


# System prompts for supervisor behavior
UNEDITABLE_SYSTEM_PROMPT = """\nYou can invoke specialist agents by calling tools in this format:
`delegate_to_<name>(user_query)` - replacing <name> with the agent's name.

Available specialist agents:
- math_agent: For mathematical calculations, arithmetic, algebra, and numerical operations
- text_agent: For text processing, formatting, analysis, and manipulation

Always delegate to the appropriate specialist rather than attempting tasks yourself.
The user will see all messages and tool calls from the specialists.
Never repeat information already provided by the specialists - just coordinate and synthesize results.
"""

DEFAULT_SUPERVISOR_PROMPT = """You are an AI supervisor managing a team of specialist agents.
For each user request, analyze what type of task it is and delegate to the appropriate specialist:

- Mathematical problems, calculations, equations, numerical analysis → delegate to math_agent
- Text processing, formatting, string manipulation, content analysis → delegate to text_agent

If a request involves both types of tasks, break it down and delegate each part appropriately.
Always provide a helpful summary that connects the specialists' responses to the user's original question.
"""


class AgentConfig(BaseModel):
    """Configuration for a remote specialist agent."""
    deployment_url: str = Field(
        description="URL of the LangGraph server hosting the agent"
    )
    agent_id: str = Field(
        description="The graph name/ID for the agent"
    )
    name: str = Field(
        description="Display name for the agent (used in delegation tools)"
    )


class SupervisorConfig(BaseModel):
    """Configuration schema for Multi-Agent Supervisor with x_oap_ui_config metadata."""
    
    agents: List[AgentConfig] = Field(
        default=[
            AgentConfig(
                deployment_url="http://localhost:2025",
                agent_id="math_agent",
                name="math_agent"
            ),
            AgentConfig(
                deployment_url="http://localhost:2026", 
                agent_id="text_agent",
                name="text_agent"
            )
        ],
        metadata={
            "x_oap_ui_config": {
                "type": "agents",
                "description": "Configure the specialist agents to manage and coordinate"
            }
        }
    )
    
    supervisor_model: str = Field(
        default="anthropic:claude-3-5-sonnet-latest",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "Model for the supervisor's decision making and coordination",
                "options": [
                    {"label": "Claude 3.5 Sonnet (Default & Recommended)", "value": "anthropic:claude-3-5-sonnet-latest"},
                    {"label": "Claude 3.5 Haiku (Faster)", "value": "anthropic:claude-3-5-haiku-latest"},
                    {"label": "GPT-4o (Recommended for supervision)", "value": "openai:gpt-4o"},
                    {"label": "GPT-4o Mini (Faster, cost-effective)", "value": "openai:gpt-4o-mini"},
                ]
            }
        }
    )
    
    temperature: float = Field(
        default=0.2,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Controls creativity in routing decisions (0.0 = consistent, 1.0 = creative)"
            }
        }
    )
    
    system_prompt: str = Field(
        default=DEFAULT_SUPERVISOR_PROMPT,
        metadata={
            "x_oap_ui_config": {
                "type": "textarea",
                "placeholder": "Enter supervisor instructions...",
                "description": f"How the supervisor should analyze and route tasks. This prompt will be appended:\n---{UNEDITABLE_SYSTEM_PROMPT}---"
            }
        }
    )
    
    max_delegation_depth: int = Field(
        default=5,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "min": 1,
                "max": 10,
                "description": "Maximum number of agent delegations per conversation turn"
            }
        }
    )
    
    routing_strategy: str = Field(
        default="intelligent",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "How the supervisor should decide which agent to use",
                "options": [
                    {"label": "Intelligent (LLM decides)", "value": "intelligent"},
                    {"label": "Keyword-based (Simple rules)", "value": "keyword"},
                    {"label": "User choice (Ask user)", "value": "user_choice"},
                ]
            }
        }
    )
    
    coordination_style: str = Field(
        default="collaborative",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "How the supervisor coordinates multiple agents",
                "options": [
                    {"label": "Collaborative (Synthesize results)", "value": "collaborative"},
                    {"label": "Sequential (One after another)", "value": "sequential"},
                    {"label": "Parallel (When possible)", "value": "parallel"},
                ]
            }
        }
    )
    
    provide_context: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "description": "Provide context about which agents are being used and why"
            }
        }
    )


def create_child_graphs(cfg: SupervisorConfig, access_token: Optional[str] = None) -> List[RemoteGraph]:
    """Create RemoteGraph instances for each configured agent."""
    if not cfg.agents:
        return []
    
    # Headers for authentication (if needed)
    headers = {}
    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-supabase-access-token": access_token
        }
    
    child_graphs = []
    for agent_config in cfg.agents:
        # Sanitize agent name for tool creation (RemoteGraph requirement)
        sanitized_name = re.sub(r'[<|\\/>]', '', agent_config.name.replace(' ', '_'))
        
        remote_graph = RemoteGraph(
            agent_config.agent_id,
            url=agent_config.deployment_url,
            name=sanitized_name,
            headers=headers if headers else None
        )
        child_graphs.append(remote_graph)
        print(f"Created RemoteGraph for {sanitized_name} at {agent_config.deployment_url}")
    
    return child_graphs


def get_api_key_for_model(model_name: str, config: RunnableConfig) -> str:
    """Extract API key from config or environment variables."""
    model_name = model_name.lower()
    if model_name.startswith("openai:"):
        key_name = "OPENAI_API_KEY"
    elif model_name.startswith("anthropic:"):
        key_name = "ANTHROPIC_API_KEY"
    else:
        return "No token found"
    
    # Try config first, then environment
    api_keys = config.get("configurable", {}).get("apiKeys", {})
    return api_keys.get(key_name) or os.getenv(key_name, "No token found")


def build_enhanced_supervisor_prompt(cfg: SupervisorConfig) -> str:
    """Build supervisor prompt based on configuration."""
    prompt = cfg.system_prompt
    
    # Add routing strategy instructions
    if cfg.routing_strategy == "keyword":
        prompt += "\n\nUSE KEYWORD-BASED ROUTING: Look for mathematical keywords (calculate, add, multiply, etc.) for math_agent, and text keywords (format, convert, analyze text, etc.) for text_agent."
    elif cfg.routing_strategy == "user_choice":
        prompt += "\n\nASK USER FOR CHOICE: When the task could be handled by multiple agents, ask the user which specialist they prefer."
    # intelligent is default behavior
    
    # Add coordination style instructions
    if cfg.coordination_style == "sequential":
        prompt += "\n\nUSE SEQUENTIAL COORDINATION: Complete one agent's task fully before moving to the next."
    elif cfg.coordination_style == "parallel":
        prompt += "\n\nUSE PARALLEL COORDINATION: When possible, delegate multiple independent tasks simultaneously."
    # collaborative is default behavior
    
    # Add context instructions
    if cfg.provide_context:
        prompt += "\n\nPROVIDE CONTEXT: Explain which specialist agents you're using and why they're the right choice for each task."
    
    # Add delegation limits
    prompt += f"\n\nDELEGATION LIMIT: Do not exceed {cfg.max_delegation_depth} agent calls per conversation turn."
    
    # Add the uneditable system prompt
    prompt += UNEDITABLE_SYSTEM_PROMPT
    
    return prompt


def graph(config: RunnableConfig):
    """Create the Multi-Agent Supervisor graph with RemoteGraph communication."""
    cfg = SupervisorConfig(**config.get("configurable", {}))
    logger = AgentLogger("supervisor")
    
    # Log configuration
    logger.log_invocation({}, config)
    
    try:
        # Get system configuration
        system_config = SystemConfig.from_environment()
        available_agents = system_config.get_available_agents()
        
        # Log debug info
        print(f"DEBUG: System config: {system_config.dict()}")
        print(f"DEBUG: Available agents: {len(available_agents)}")
        
        if not available_agents:
            # For now, create default agents even if health check fails
            # This allows the supervisor to work even if health checks are unreliable in server context
            print("WARNING: Health check failed, using default agent configuration")
            available_agents = [
                AgentEndpoint(name="math_agent", url="http://localhost:2025", agent_id="math_agent"),
                AgentEndpoint(name="text_agent", url="http://localhost:2026", agent_id="text_agent")
            ]
            logger.log_error("Health check failed, using default configuration")
        
        # Get access token if available (for authenticated remote calls)
        access_token = config.get("configurable", {}).get("x-supabase-access-token")
        
        # Create RemoteGraph instances for available agents only
        child_graphs = []
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else None
        
        for agent_endpoint in available_agents:
            sanitized_name = re.sub(r'[<|\\/>]', '', agent_endpoint.name.replace(' ', '_'))
            remote_graph = RemoteGraph(
                agent_endpoint.agent_id,
                url=agent_endpoint.url,
                name=sanitized_name,
                headers=headers
            )
            child_graphs.append(remote_graph)
            logger.logger.info(f"Added healthy agent: {agent_endpoint.name}")
        
        # Create supervisor model with configuration
        model = init_chat_model(
            cfg.supervisor_model,
            temperature=cfg.temperature,
            api_key=get_api_key_for_model(cfg.supervisor_model, config)
        )
        
        # Build complete prompt with configuration
        full_prompt = build_enhanced_supervisor_prompt(cfg)
        
        print(f"Creating supervisor with {len(child_graphs)} healthy agents:")
        for child in child_graphs:
            print(f"  - {child.name}")
        
        # Create supervisor using langgraph-supervisor
        return create_supervisor(
            child_graphs,
            model=model,
            prompt=full_prompt,
            config_schema=SupervisorConfig,
            handoff_tool_prefix="delegate_to_",
            output_mode="full_history"  # Include all agent interactions in output
        )
        
    except Exception as e:
        logger.log_error(str(e), {"config": cfg.dict()})
        raise