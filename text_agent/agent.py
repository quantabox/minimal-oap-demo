"""
Text Processing Agent - Configuration-driven agent with text manipulation tools
Demonstrates x_oap_ui_config patterns for dynamic UI generation
"""

import os
import re
from typing import Optional, List
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
import hashlib
import base64


@tool
def convert_case(text: str, case_type: str) -> str:
    """Convert text to different cases: upper, lower, title, capitalize."""
    case_type = case_type.lower()
    if case_type == "upper":
        return text.upper()
    elif case_type == "lower":
        return text.lower()
    elif case_type == "title":
        return text.title()
    elif case_type == "capitalize":
        return text.capitalize()
    else:
        return f"Unknown case type: {case_type}. Options: upper, lower, title, capitalize"


@tool
def count_words(text: str) -> str:
    """Count words, characters, and lines in text."""
    words = len(text.split())
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    lines = len(text.split("\n"))
    
    return f"Words: {words}, Characters: {chars}, Characters (no spaces): {chars_no_spaces}, Lines: {lines}"


@tool
def reverse_text(text: str) -> str:
    """Reverse the given text."""
    return text[::-1]


@tool
def extract_emails(text: str) -> str:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    if emails:
        return f"Found {len(emails)} email(s): {', '.join(emails)}"
    else:
        return "No email addresses found"


@tool
def clean_whitespace(text: str) -> str:
    """Remove extra whitespace and normalize spacing."""
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    return cleaned


@tool
def hash_text(text: str, algorithm: str = "md5") -> str:
    """Generate hash of text using specified algorithm (md5, sha1, sha256)."""
    algorithm = algorithm.lower()
    
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        return f"Unknown algorithm: {algorithm}. Options: md5, sha1, sha256"


@tool
def encode_base64(text: str) -> str:
    """Encode text to base64."""
    encoded = base64.b64encode(text.encode()).decode()
    return f"Base64 encoded: {encoded}"


@tool
def decode_base64(encoded_text: str) -> str:
    """Decode base64 text."""
    try:
        decoded = base64.b64decode(encoded_text).decode()
        return f"Base64 decoded: {decoded}"
    except Exception as e:
        return f"Error decoding base64: {str(e)}"


class TextAgentConfig(BaseModel):
    """Configuration schema for Text Processing Agent with x_oap_ui_config metadata."""
    
    model_name: str = Field(
        default="anthropic:claude-3-5-haiku-latest",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "Choose the LLM model for text processing tasks",
                "options": [
                    {"label": "Claude 3.5 Haiku (Fast & Default)", "value": "anthropic:claude-3-5-haiku-latest"},
                    {"label": "Claude 3.5 Sonnet (Most Capable)", "value": "anthropic:claude-3-5-sonnet-latest"},
                    {"label": "GPT-4o Mini (Fast & Efficient)", "value": "openai:gpt-4o-mini"},
                    {"label": "GPT-4o (Most Capable)", "value": "openai:gpt-4o"},
                ]
            }
        }
    )
    
    temperature: float = Field(
        default=0.3,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Controls creativity in text processing (0.0 = precise, 1.0 = creative)"
            }
        }
    )
    
    max_output_length: int = Field(
        default=1000,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "min": 100,
                "max": 5000,
                "description": "Maximum length of processed text output"
            }
        }
    )
    
    preserve_formatting: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "description": "Preserve original text formatting when possible"
            }
        }
    )
    
    enabled_tools: list = Field(
        default=["convert_case", "count_words", "reverse_text", "extract_emails", "clean_whitespace"],
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "multiple": True,
                "description": "Select which text processing tools to enable",
                "options": [
                    {"label": "Case Conversion", "value": "convert_case"},
                    {"label": "Word/Character Counting", "value": "count_words"},
                    {"label": "Text Reversal", "value": "reverse_text"},
                    {"label": "Email Extraction", "value": "extract_emails"},
                    {"label": "Whitespace Cleaning", "value": "clean_whitespace"},
                    {"label": "Text Hashing", "value": "hash_text"},
                    {"label": "Base64 Encoding", "value": "encode_base64"},
                    {"label": "Base64 Decoding", "value": "decode_base64"},
                ]
            }
        }
    )
    
    processing_mode: str = Field(
        default="helpful",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "How the agent should approach text processing tasks",
                "options": [
                    {"label": "Helpful (Explain and process)", "value": "helpful"},
                    {"label": "Efficient (Just process)", "value": "efficient"},
                    {"label": "Educational (Explain concepts)", "value": "educational"},
                ]
            }
        }
    )
    
    system_prompt: str = Field(
        default="You are a helpful text processing assistant. Help users manipulate, analyze, and transform text efficiently and accurately.",
        metadata={
            "x_oap_ui_config": {
                "type": "textarea",
                "placeholder": "Enter system prompt for the text agent...",
                "description": "Instructions for how the agent should behave and process text"
            }
        }
    )
    
    output_style: str = Field(
        default="structured",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "description": "How to format text processing results",
                "options": [
                    {"label": "Structured (organized output)", "value": "structured"},
                    {"label": "Natural (conversational)", "value": "natural"},
                    {"label": "Technical (detailed info)", "value": "technical"},
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
        "convert_case": convert_case,
        "count_words": count_words,
        "reverse_text": reverse_text,
        "extract_emails": extract_emails,
        "clean_whitespace": clean_whitespace,
        "hash_text": hash_text,
        "encode_base64": encode_base64,
        "decode_base64": decode_base64,
    }
    
    return [all_tools[name] for name in enabled_tool_names if name in all_tools]


def build_enhanced_prompt(config: TextAgentConfig) -> str:
    """Build system prompt based on configuration."""
    prompt = config.system_prompt
    
    # Add output length constraints
    prompt += f"\n\nIMPORTANT: Keep processed text outputs under {config.max_output_length} characters when possible."
    
    # Add formatting preferences
    if config.preserve_formatting:
        prompt += " Preserve original text formatting, line breaks, and structure when processing text."
    else:
        prompt += " Feel free to reformat text for clarity and readability."
    
    # Add processing mode instructions
    if config.processing_mode == "helpful":
        prompt += " Be helpful by explaining what you're doing and why, then provide the processed result."
    elif config.processing_mode == "efficient":
        prompt += " Focus on efficiently processing the text with minimal explanation."
    elif config.processing_mode == "educational":
        prompt += " Explain text processing concepts and teach users about the operations you perform."
    
    # Add output style instructions
    if config.output_style == "structured":
        prompt += " Present results in a clear, organized format with headers and sections."
    elif config.output_style == "natural":
        prompt += " Present results in a natural, conversational manner."
    elif config.output_style == "technical":
        prompt += " Provide detailed technical information about the processing operations."
    
    return prompt


def graph(config: RunnableConfig):
    """Create the Text Processing Agent graph with configuration-driven behavior."""
    cfg = TextAgentConfig(**config.get("configurable", {}))
    
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
    tool_node = ToolNode(tools, handle_tool_errors="Text processing failed. Please try a different approach or simpler input.")
    
    return create_react_agent(
        model=model,
        tools=tool_node,
        prompt=enhanced_prompt,
        config_schema=TextAgentConfig
    )