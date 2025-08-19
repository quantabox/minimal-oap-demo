"""
Simple environment-based configuration management
"""
import os
from typing import List, Optional
from pydantic import BaseModel, validator
import requests

class AgentEndpoint(BaseModel):
    name: str
    url: str
    agent_id: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    def is_healthy(self) -> bool:
        """Simple health check - just connectivity"""
        try:
            response = requests.get(f"{self.url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False

class SystemConfig(BaseModel):
    math_agent_url: str = "http://localhost:2025"
    text_agent_url: str = "http://localhost:2026"
    supervisor_port: int = 2024
    
    @classmethod
    def from_environment(cls):
        return cls(
            math_agent_url=os.getenv("MATH_AGENT_URL", "http://localhost:2025"),
            text_agent_url=os.getenv("TEXT_AGENT_URL", "http://localhost:2026"),
            supervisor_port=int(os.getenv("SUPERVISOR_PORT", "2024"))
        )
    
    def get_available_agents(self) -> List[AgentEndpoint]:
        """Get list of available agents with health checking"""
        agents = [
            AgentEndpoint(name="math_agent", url=self.math_agent_url, agent_id="math_agent"),
            AgentEndpoint(name="text_agent", url=self.text_agent_url, agent_id="text_agent")
        ]
        
        available = []
        for agent in agents:
            if agent.is_healthy():
                available.append(agent)
                print(f"✅ {agent.name} healthy at {agent.url}")
            else:
                print(f"⚠️ {agent.name} not available at {agent.url}")
        
        return available