# Minimal OAP Demo - Configuration-Driven Multi-Agent System

This demo recreates the core capabilities of the Open Agent Platform (OAP) using local LangGraph deployments. It showcases:

- **Configuration-driven agents** using `x_oap_ui_config` metadata patterns
- **RemoteGraph communication** for distributed agent coordination  
- **Multi-agent supervision** with intelligent request routing
- **Local deployment** without cloud dependencies

## Architecture

```mermaid
graph TB
    User[👤 User] --> Supervisor[🎯 Supervisor Agent<br/>Port 2024]
    
    Supervisor --> |delegate_to_math_agent| MathAgent[🔢 Math Agent<br/>Port 2025]
    Supervisor --> |delegate_to_text_agent| TextAgent[📝 Text Agent<br/>Port 2026]
    
    MathAgent --> MathTools[➕ Math Tools<br/>add, multiply, sqrt, power]
    TextAgent --> TextTools[📄 Text Tools<br/>case, count, reverse, clean]
    
    subgraph "Local LangGraph Servers"
        Supervisor
        MathAgent  
        TextAgent
    end
```

## Quick Start

### 1. Configure API Keys
Copy and edit the environment file:
```bash
cp .env.example .env
# Edit .env with your actual API keys:
# OPENAI_API_KEY=sk-your_actual_openai_key_here
# ANTHROPIC_API_KEY=sk-ant-your_actual_anthropic_key_here
```

### 2. Install Dependencies with UV
```bash
uv sync
```

### 3. Start All Agents
```bash
./start_agents.sh
```

This starts three LangGraph servers:
- **Math Agent**: `http://localhost:2025`
- **Text Agent**: `http://localhost:2026` 
- **Supervisor Agent**: `http://localhost:2024`

### 4. Test the System
```bash
uv run python test_demo.py
```

### 5. Stop All Agents
```bash
./stop_agents.sh
```

## Agent Configurations

### Math Agent (`x_oap_ui_config` Examples)

```python
class MathAgentConfig(BaseModel):
    precision: int = Field(
        default=3,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "min": 0, "max": 10,
                "description": "Decimal places for results"
            }
        }
    )
    
    show_work: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean", 
                "description": "Show calculation steps"
            }
        }
    )
    
    enabled_tools: list = Field(
        default=["add_numbers", "multiply_numbers"],
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "multiple": True,
                "options": [
                    {"label": "Addition", "value": "add_numbers"},
                    {"label": "Multiplication", "value": "multiply_numbers"}
                ]
            }
        }
    )
```

### Text Agent Configuration

```python
class TextAgentConfig(BaseModel):
    temperature: float = Field(
        default=0.3,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "min": 0.0, "max": 1.0, "step": 0.1,
                "description": "Creativity in text processing"
            }
        }
    )
    
    processing_mode: str = Field(
        default="helpful",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "options": [
                    {"label": "Helpful (Explain)", "value": "helpful"},
                    {"label": "Efficient (Direct)", "value": "efficient"}
                ]
            }
        }
    )
```

### Supervisor Configuration

```python
class SupervisorConfig(BaseModel):
    agents: List[AgentConfig] = Field(
        metadata={
            "x_oap_ui_config": {
                "type": "agents",  # Special OAP UI type
                "description": "Configure specialist agents"
            }
        }
    )
    
    routing_strategy: str = Field(
        default="intelligent",
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "options": [
                    {"label": "Intelligent (LLM)", "value": "intelligent"},
                    {"label": "Keyword-based", "value": "keyword"}
                ]
            }
        }
    )
```

## Usage Examples

### Direct Agent Usage

```python
from langgraph_sdk import get_client

# Math Agent
math_client = get_client(url="http://localhost:2025")
response = await math_client.runs.create(
    assistant_id="math_agent",
    input={"messages": [{"role": "user", "content": "What is 25 + 17?"}]},
    config={"configurable": {"precision": 3, "show_work": True}}
)

# Text Agent
text_client = get_client(url="http://localhost:2026")
response = await text_client.runs.create(
    assistant_id="text_agent", 
    input={"messages": [{"role": "user", "content": "Convert to uppercase: hello"}]},
    config={"configurable": {"processing_mode": "helpful"}}
)
```

### Multi-Agent Coordination

```python
# Supervisor automatically routes to appropriate agents
supervisor_client = get_client(url="http://localhost:2024")
response = await supervisor_client.runs.create(
    assistant_id="supervisor",
    input={"messages": [{"role": "user", "content": "Calculate 8 squared and convert result to uppercase"}]},
    config={"configurable": {
        "routing_strategy": "intelligent",
        "agents": [
            {"deployment_url": "http://localhost:2025", "agent_id": "math_agent", "name": "math_agent"},
            {"deployment_url": "http://localhost:2026", "agent_id": "text_agent", "name": "text_agent"}
        ]
    }}
)
```

## Key Features Demonstrated

### 1. Configuration-Driven UI Generation
- `x_oap_ui_config` metadata automatically generates UI components
- Supports: `select`, `slider`, `number`, `boolean`, `textarea`, `agents`
- Runtime configuration changes agent behavior

### 2. RemoteGraph Communication  
- Agents communicate over HTTP using LangGraph's RemoteGraph
- Location transparency - remote agents appear local
- Automatic state synchronization across distributed agents

### 3. Multi-Agent Coordination
- Supervisor intelligently routes requests to specialist agents
- Auto-generated delegation tools: `delegate_to_math_agent()`, `delegate_to_text_agent()`
- Context preservation across agent boundaries

### 4. Thread-Based State Management
- Conversation history maintained across multiple interactions
- State shared between supervisor and specialist agents
- Persistent context without manual state management

## API Endpoints

Once running, explore the agent APIs:

- **Math Agent API**: `http://localhost:2025/docs`
- **Text Agent API**: `http://localhost:2026/docs` 
- **Supervisor API**: `http://localhost:2024/docs`

## LangGraph Studio (Optional)

Connect to LangGraph Studio for visual debugging:

- **Math Agent**: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2025`
- **Text Agent**: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2026`
- **Supervisor**: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`

## Implementation Notes

### No Cloud Dependencies
- Uses local LangGraph dev servers (`langgraph dev`)
- No LangGraph Platform or cloud services required
- Only needs LLM API keys for model access

### OAP Pattern Fidelity
- Implements exact `x_oap_ui_config` metadata patterns from OAP
- Uses standard LangGraph `RemoteGraph` for agent communication
- Follows OAP's supervisor delegation model precisely

### Extensibility
- Easy to add new agents by following existing patterns
- Configuration schemas are fully customizable
- Tool integration follows standard LangGraph patterns

This demonstrates that OAP's core capabilities can be fully recreated using open-source LangGraph without any vendor lock-in or cloud dependencies.