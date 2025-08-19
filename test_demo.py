#!/usr/bin/env python3
"""
Test script to demonstrate minimal OAP capabilities
Shows configuration-driven agents and RemoteGraph communication
"""

import asyncio
import json
from langgraph_sdk import get_client


async def test_math_agent():
    """Test the math agent directly."""
    print("🔢 Testing Math Agent (Port 2025)")
    print("=" * 50)
    
    client = get_client(url="http://localhost:2025")
    
    # Test with different configurations
    configs = [
        {
            "model_name": "anthropic:claude-3-5-haiku-latest",
            "precision": 3,
            "show_work": True,
            "response_style": "detailed",
            "enabled_tools": ["add_numbers", "square_root"]
        },
        {
            "model_name": "anthropic:claude-3-5-haiku-latest",
            "precision": 1,
            "show_work": False,
            "response_style": "concise",
            "enabled_tools": ["multiply_numbers", "power"]
        }
    ]
    
    test_messages = [
        "What is 25 + 17?",
        "Calculate the square root of 144",
        "What is 5 times 8?",
        "What is 2 to the power of 8?"
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n📋 Configuration {i}:")
        print(f"   Precision: {config['precision']}, Show work: {config['show_work']}")
        print(f"   Style: {config['response_style']}, Tools: {config['enabled_tools']}")
        
        thread = await client.threads.create()
        
        for message in test_messages[:2]:  # Test 2 messages per config
            print(f"\n❓ User: {message}")
            
            response = await client.runs.create(
                thread_id=thread['thread_id'],
                assistant_id="math_agent",
                input={"messages": [{"role": "user", "content": message}]},
                config={"configurable": config}
            )
            
            # Wait for completion
            await client.runs.join(thread['thread_id'], response['run_id'])
            
            # Get the final state
            state = await client.threads.get_state(thread_id=thread['thread_id'])
            last_message = state['values']['messages'][-1]['content']
            print(f"🤖 Math Agent: {last_message}")


async def test_text_agent():
    """Test the text agent directly."""
    print("\n\n📝 Testing Text Agent (Port 2026)")
    print("=" * 50)
    
    client = get_client(url="http://localhost:2026")
    
    # Test with different configurations
    config = {
        "model_name": "anthropic:claude-3-5-haiku-latest",
        "temperature": 0.1,
        "preserve_formatting": True,
        "processing_mode": "helpful",
        "enabled_tools": ["convert_case", "count_words", "reverse_text", "clean_whitespace"]
    }
    
    test_messages = [
        "Convert this text to uppercase: hello world",
        "Count the words in: The quick brown fox jumps over the lazy dog",
        "Reverse this text: Hello OpenAI",
        "Clean up this text:   too    many     spaces   here   "
    ]
    
    print(f"\n📋 Configuration:")
    print(f"   Temperature: {config['temperature']}, Mode: {config['processing_mode']}")
    print(f"   Tools: {config['enabled_tools']}")
    
    thread = await client.threads.create()
    
    for message in test_messages:
        print(f"\n❓ User: {message}")
        
        response = await client.runs.create(
            thread_id=thread['thread_id'],
            assistant_id="text_agent",
            input={"messages": [{"role": "user", "content": message}]},
            config={"configurable": config}
        )
        
        # Wait for completion
        await client.runs.join(thread['thread_id'], response['run_id'])
        
        # Get the final state
        state = await client.threads.get_state(thread_id=thread['thread_id'])
        last_message = state['values']['messages'][-1]['content']
        print(f"🤖 Text Agent: {last_message}")


async def test_supervisor():
    """Test the multi-agent supervisor."""
    print("\n\n🎯 Testing Supervisor Agent (Port 2024)")
    print("=" * 50)
    
    client = get_client(url="http://localhost:2024")
    
    # Supervisor configuration
    config = {
        "supervisor_model": "anthropic:claude-3-5-sonnet-latest",
        "temperature": 0.2,
        "routing_strategy": "intelligent",
        "coordination_style": "collaborative",
        "provide_context": True,
        "agents": [
            {
                "deployment_url": "http://localhost:2025",
                "agent_id": "math_agent", 
                "name": "math_agent"
            },
            {
                "deployment_url": "http://localhost:2026",
                "agent_id": "text_agent",
                "name": "text_agent"
            }
        ]
    }
    
    # Test messages that require different agents
    test_messages = [
        "What is 15 + 27?",
        "Convert 'HELLO WORLD' to lowercase",
        "Calculate 8 squared and then count the words in the result",
        "What is the square root of 64, and convert the answer to uppercase text?"
    ]
    
    print(f"\n📋 Supervisor Configuration:")
    print(f"   Strategy: {config['routing_strategy']}, Style: {config['coordination_style']}")
    print(f"   Managing {len(config['agents'])} agents")
    
    thread = await client.threads.create()
    
    for message in test_messages:
        print(f"\n❓ User: {message}")
        print("🎯 Supervisor analyzing and delegating...")
        
        response = await client.runs.create(
            thread_id=thread['thread_id'],
            assistant_id="supervisor",
            input={"messages": [{"role": "user", "content": message}]},
            config={"configurable": config}
        )
        
        # Wait for completion
        await client.runs.join(thread['thread_id'], response['run_id'])
        
        # Get the final state
        state = await client.threads.get_state(thread_id=thread['thread_id'])
        last_message = state['values']['messages'][-1]['content']
        print(f"🤖 Supervisor: {last_message}")
        print("-" * 40)


async def main():
    """Run all tests."""
    print("🚀 Minimal OAP Demo - Testing Configuration-Driven Multi-Agent System")
    print("=" * 80)
    
    try:
        # Test individual agents first
        await test_math_agent()
        await test_text_agent()
        
        # Test multi-agent coordination
        await test_supervisor()
        
        print("\n\n✅ All tests completed successfully!")
        print("=" * 80)
        print("\n💡 Key Demonstrations:")
        print("   • Configuration-driven agent behavior (x_oap_ui_config patterns)")
        print("   • Tool selection and parameterization")
        print("   • RemoteGraph communication between agents")
        print("   • Multi-agent coordination and delegation")
        print("   • Thread-based conversation persistence")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n🔧 Make sure all agents are running:")
        print("   ./start_agents.sh")


if __name__ == "__main__":
    asyncio.run(main())