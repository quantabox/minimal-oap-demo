"""
Math Agent - Configuration-driven agent with mathematical tools
Demonstrates x_oap_ui_config patterns for dynamic UI generation
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
import math


@tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result}"


@tool
def multiply_numbers(a: float, b: float) -> str:
    """Multiply two numbers together."""
    result = a * b
    return f"{a} × {b} = {result}"


@tool
def square_root(number: float) -> str:
    """Calculate the square root of a number."""
    if number < 0:
        return "Error: Cannot calculate square root of negative number"
    result = math.sqrt(number)
    return f"√{number} = {result}"


@tool
def power(base: float, exponent: float) -> str:
    """Calculate base raised to the power of exponent."""
    result = base ** exponent
    return f"{base}^{exponent} = {result}"


@tool
def factorial(n: int) -> str:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        return "Error: Factorial is not defined for negative numbers"
    if n > 20:
        return "Error: Factorial too large (limit: 20)"
    
    result = math.factorial(n)
    return f"{n}! = {result}"


class MathAgentConfig(BaseModel):
    """Configuration schema for Math Agent with x_oap_ui_config metadata."""
    
    model_name: str = Field(
        default="anthropic:claude-3-5-haiku-latest",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "Choose the LLM model for mathematical reasoning",
                "options": [
                    {"label": "Claude 3.5 Haiku (Fast & Default)", "value": "anthropic:claude-3-5-haiku-latest"},
                    {"label": "Claude 3.5 Sonnet (Most Capable)", "value": "anthropic:claude-3-5-sonnet-latest"},
                    {"label": "GPT-4o Mini (Fast & Cost-effective)", "value": "openai:gpt-4o-mini"},
                    {"label": "GPT-4o (Most Capable)", "value": "openai:gpt-4o"},
                ]
            }
        }
    )
    
    temperature: float = Field(
        default=0.1,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Controls randomness in responses (0.0 = deterministic, 1.0 = creative)"
            }
        }
    )
    
    precision: int = Field(
        default=3,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "min": 0,
                "max": 10,
                "description": "Number of decimal places for results"
            }
        }
    )
    
    show_work: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "description": "Show detailed calculation steps in responses"
            }
        }
    )
    
    enabled_tools: list = Field(
        default=["add_numbers", "multiply_numbers", "square_root", "power", "factorial"],
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "multiple": True,
                "description": "Select which mathematical tools to enable",
                "options": [
                    {"label": "Addition", "value": "add_numbers"},
                    {"label": "Multiplication", "value": "multiply_numbers"},
                    {"label": "Square Root", "value": "square_root"},
                    {"label": "Power/Exponent", "value": "power"},
                    {"label": "Factorial", "value": "factorial"},
                ]
            }
        }
    )
    
    system_prompt: str = Field(
        default="You are a helpful mathematical assistant. Solve problems step by step, show your work clearly, and explain mathematical concepts when helpful.",
        metadata={
            "x_oap_ui_config": {
                "type": "textarea",
                "placeholder": "Enter system prompt for the math agent...",
                "description": "Instructions for how the agent should behave and respond"
            }
        }
    )
    
    output_format: str = Field(
        default="detailed",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "How to format mathematical responses",
                "options": [
                    {"label": "Detailed with explanations", "value": "detailed"},
                    {"label": "Concise results only", "value": "concise"},
                    {"label": "Step-by-step breakdown", "value": "steps"},
                ]
            }
        }
    )


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


def get_enabled_tools(enabled_tool_names: list):
    """Return only the tools that are enabled in configuration."""
    all_tools = {
        "add_numbers": add_numbers,
        "multiply_numbers": multiply_numbers,
        "square_root": square_root,
        "power": power,
        "factorial": factorial,
    }
    
    return [all_tools[name] for name in enabled_tool_names if name in all_tools]


def build_enhanced_prompt(config: MathAgentConfig) -> str:
    """Build system prompt based on configuration."""
    prompt = config.system_prompt
    
    # Add precision instructions
    prompt += f"\n\nIMPORTANT: Round all numerical results to {config.precision} decimal places."
    
    # Add work-showing instructions
    if config.show_work:
        prompt += " Always show your calculation steps and explain your reasoning."
    else:
        prompt += " Provide direct answers without showing intermediate steps."
    
    # Add output format instructions
    if config.output_format == "detailed":
        prompt += " Provide detailed explanations and context for mathematical concepts."
    elif config.output_format == "concise":
        prompt += " Keep responses brief and focused on the final result."
    elif config.output_format == "steps":
        prompt += " Break down solutions into clear, numbered steps."
    
    return prompt


def graph(config: RunnableConfig):
    """Create the Math Agent graph with configuration-driven behavior."""
    cfg = MathAgentConfig(**config.get("configurable", {}))
    
    # Get enabled tools based on configuration
    tools = get_enabled_tools(cfg.enabled_tools)
    
    # Build enhanced prompt
    enhanced_prompt = build_enhanced_prompt(cfg)
    
    # Initialize model with configuration
    model = init_chat_model(
        cfg.model_name,
        temperature=cfg.temperature,
        api_key=get_api_key_for_model(cfg.model_name, config)
    )
    
    # Create tool node with error handling
    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode(tools, handle_tool_errors="Math operation failed. Please check your input and try again.")
    
    return create_react_agent(
        model=model,
        tools=tool_node,
        prompt=enhanced_prompt,
        config_schema=MathAgentConfig
    )