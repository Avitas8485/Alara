from typing import Dict, List, Any 
from enum import Enum
from datetime import datetime as dt


class ToolStatus(Enum):
    """An enumeration of possible tool statuses."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class Tool:
    def __init__(self, name: str, description: str, usage: str):
        """A tool is an internal component of the system that performs a specific task.
        Users typically don't interact with tools directly, they are used by the system to perform tasks.
        They are used to encapsulate functionality and dependencies.
        Args:
            name (str): The name of the tool.
            description (str): A description of the tool.
            usage (str): How to use the tool.
            dependencies (Dict[str, Tool]): The dependencies of the tool.
            healthy (bool): The health status of the tool."""
        self.name = name
        self.description = description
        self.usage = usage
        self.dependencies: Dict[str, Tool] = {}
        self.status = ToolStatus.UNKNOWN
        
    def add_dependency(self, tool: 'Tool'):
        """Add a dependency to the tool.
        Args:
            tool (Tool): The tool to add as a dependency."""
        self.dependencies[tool.name] = tool
        
    def remove_dependency(self, tool_name: str):
        """Remove a dependency from the tool.
        Args:
            tool_name (str): The name of the tool to remove as a dependency."""
        if tool_name in self.dependencies:
            del self.dependencies[tool_name]
            
    def check_status(self)-> ToolStatus:
        """Check the health status of the tool."""
        if all(dependency.check_status() == ToolStatus.HEALTHY for dependency in self.dependencies.values()):
            try:
                self._run()
                self.status = ToolStatus.HEALTHY
            except Exception as e:
                self.status = ToolStatus.UNHEALTHY
                print(f"Error running tool: {self.name}, setting status to unhealthy.")
                print(e)
        else:
            self.status = ToolStatus.UNHEALTHY
        return self.status
    
    def run(self,*args, **kwargs):
        """Run the tool. This method checks the health status of the tool before running it.
        Always call this method to run the tool, rather than calling the _run method directly to properly handle the health status.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments."""
        if self.check_status() == ToolStatus.UNHEALTHY:
            raise Exception(f"Cannot run tool {self.name} because it is unhealthy")
        else:
            return self._run(*args, **kwargs)
                
    def _run(self, *args, **kwargs):
        """The actual implementation of running the tool.
    This method is intended to be private and should not be directly called.
    Instead, use the run method to run the tool.
    This method should be implemented by subclasses."""
        raise NotImplementedError()
    
    def __str__(self)-> str:
        return f"Tool Name: {self.name} Status: {self.status} @ {dt.now()}"
    
    
class ToolKit:
    """A toolkit is a collection of tools that are used by the system to perform tasks.
    It manages the dependencies between tools and ensures that tools are used correctly.
    Tools can be added, removed, and run from the toolkit.
    Attributes:
        tools (Dict[str, Tool]): A dictionary of tools in the toolkit."""
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def add_tool(self, tool: Tool):
        """Add a tool to the toolkit.
        Args:
            tool (Tool): The tool to add to the toolkit."""
        self.tools[tool.name] = tool
        
    def remove_tool(self, tool_name: str):
        """Remove a tool from the toolkit.
        Args:
            tool_name (str): The name of the tool to remove from the toolkit."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            
    
    def check_dependencies(self, tool_name: str):
        """Check the dependencies of a tool to ensure they are available and healthy.
        Args:
            tool_name (str): The name of the tool to check dependencies for."""
        if tool_name in self.tools:
            for dependency in self.tools[tool_name].dependencies:
                if dependency not in self.tools or self.tools[dependency].status != ToolStatus.HEALTHY:
                    print(f"Error: {tool_name} depends on {dependency} but the tool is not available or healthy.")
                    return False
            return True
        
    def run(self, tool_name: str, *args, **kwargs):
        """Run a tool from the toolkit.
        Args:
            tool_name (str): The name of the tool to run.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments."""
        if self.check_dependencies(tool_name):
            tool = self.tools[tool_name]
            return tool.run(*args, **kwargs)
        else:
            print(f"Error running tool: {tool_name}")
        
            
            
    def __str__(self)-> str:
        """Return a string representation of the toolkit."""
        return "\n".join([str(tool) for tool in self.tools.values()])
    
    