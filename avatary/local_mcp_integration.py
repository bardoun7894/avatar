"""
Local MCP Tools Integration for LiveKit Agent
Adapter to use local appointment tools with the agent
"""
from typing import Any, Dict, List, Callable
from livekit.agents import Agent, llm
from local_mcp_server import get_local_tools, call_tool as execute_local_tool
import inspect

class LocalToolsIntegration:
    """Integration for local appointment booking tools"""
    
    @staticmethod
    def create_function_from_tool(tool: Dict) -> Callable:
        """Create an async function from tool definition"""
        tool_name = tool["name"]
        
        # Create the async function
        async def tool_function(**kwargs):
            """Dynamically created tool function"""
            result = execute_local_tool(tool_name, kwargs)
            return result
        
        # Set function metadata
        tool_function.__name__ = tool_name
        tool_function.__doc__ = tool["description"]
        
        return tool_function
    
    @staticmethod
    def get_tools_for_agent() -> List[Callable]:
        """Get list of tool functions for the agent"""
        local_tools = get_local_tools()
        agent_functions = []
        
        for tool in local_tools:
            # Create callable function
            func = LocalToolsIntegration.create_function_from_tool(tool)
            agent_functions.append(func)
        
        return agent_functions
    
    @staticmethod
    async def create_agent_with_tools(agent_class) -> Agent:
        """Create an agent instance with local tools"""
        # Create agent instance
        agent = agent_class()
        
        # Get local tools
        local_tools = get_local_tools()
        
        # Register each tool with the agent
        for tool in local_tools:
            func = LocalToolsIntegration.create_function_from_tool(tool)
            
            # The Agent class should have methods to register functions
            # For now, we'll just attach them as attributes
            setattr(agent, tool["name"], func)
        
        return agent

