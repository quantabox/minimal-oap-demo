"""
Simple logging utility for agent interactions
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any


def safe_serialize(obj):
    """Safely serialize objects to JSON, handling non-serializable types."""
    try:
        return json.loads(json.dumps(obj))
    except (TypeError, ValueError):
        # Handle non-serializable objects
        if hasattr(obj, '__dict__'):
            try:
                return str(obj)
            except:
                return f"<{type(obj).__name__}>"
        else:
            return str(type(obj).__name__)

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agents.log'),
        logging.StreamHandler()
    ]
)

class AgentLogger:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
    
    def log_invocation(self, input_data: Dict[str, Any], config: Dict[str, Any] = None):
        """Log agent invocation with basic metrics"""
        safe_config = safe_serialize(config.get("configurable", {}) if config else {})
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "event": "invocation",
            "config": safe_config,
            "message_count": len(input_data.get("messages", []))
        }))
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log errors with context"""
        safe_context = safe_serialize(context or {})
        self.logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "event": "error",
            "error": error,
            "context": safe_context
        }))
    
    def log_delegation(self, to_agent: str, query_preview: str):
        """Log supervisor delegations"""
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "event": "delegation",
            "to_agent": to_agent,
            "query_preview": query_preview[:100] + "..." if len(query_preview) > 100 else query_preview
        }))