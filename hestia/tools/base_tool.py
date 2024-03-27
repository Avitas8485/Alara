from typing import Dict, List, Any 

class Tool:
    def __init__(self, name: str, description: str, usage: str):
        self.name = name
        self.description = description
        self.usage = usage
        self.dependencies: Dict[str, Tool] = {}

    
    def run(self,*args, **kwargs):
        raise NotImplementedError()
    
    def __str__(self)-> str:
        return f"{self.name}: {self.description}"
    
    
class ToolKit:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        
    def remove_tool(self, tool_name: str):
        if tool_name in self.tools:
            del self.tools[tool_name]
            
    
    def check_dependencies(self, tool_name: str):
        if tool_name in self.tools:
            for dependency in self.tools[tool_name].dependencies:
                if dependency not in self.tools:
                    print(f"Error: {tool_name} depends on {dependency}")
                    return False
            return True
        
    def run(self, tool_name: str, *args, **kwargs):
        if self.check_dependencies(tool_name):
            tool = self.tools[tool_name]
            return tool.run(*args, **kwargs)
        else:
            print(f"Error running tool: {tool_name}")
        
            
            
    def __str__(self)-> str:
        return "\n".join([str(tool) for tool in self.tools.values()])
    
    