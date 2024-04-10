from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from uuid import uuid4
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any, Optional
from hestia.tools.base_tool import Tool, ToolKit
from hestia.tools.text_parser.text_splitter import split_text

class MemoryType(str, Enum):
    THOUGHT = 'thought'
    KNOWLEDGE = 'knowledge'
    DIALOGUE = 'dialogue'
    

class Memory(BaseModel):
    memory_type: MemoryType = Field(..., description='What would you classify this memory as?')
    source: str = Field(..., description='Where did this memory come from? this can range from a book, knowledge base, observation, etc.')
    content: str = Field(..., description='Content of the memory, this can be a thought, a piece of knowledge, a dialogue, etc.')
    

    





PERSISTENT_DIRECTORY = '/hestia/tools/memory/chroma/db/'
COLLECTION_NAME = 'Alara_Memories'
MODEL_NAME = 'all-MiniLM-L6-v2'

class AddMemoryTool(Tool):
    def __init__(self):
        self.name = "add_memory"
        self.description = "Store information in long term memory"
        self.usage = "add_memory [Memory]"
        self.dependencies = {}
        
    def run(self, memory: Memory):
        client = ChromaDBClient()
        client.add_memory(memory)
        return "Memory added successfully"
    
class SearchMemoryTool(Tool):
    def __init__(self):
        self.name = "search_memory"
        self.description = "Search for information in long term memory"
        self.usage = "search_memory [query]"
        self.dependencies = {}
        
    def run(self, query: str):
        client = ChromaDBClient()
        results = client.search(query, top_k=1)
        return results
    
class ChromaMemoryToolKit(ToolKit):
    def __init__(self):
        super().__init__()
        self.add_tool(AddMemoryTool())
        self.add_tool(SearchMemoryTool())
        
    def __str__(self)-> str:
        return "\n".join([str(tool) for tool in self.tools.values()])
    
    def run(self, tool_name: str, *args, **kwargs):
        if self.check_dependencies(tool_name):
            tool = self.tools[tool_name]
            return tool.run(*args, **kwargs)
        else:
            print(f"Error running tool: {tool_name}")
    
    

class ChromaDBClient():
    def __init__(self, persist_directory: str = PERSISTENT_DIRECTORY, collection_name: str = COLLECTION_NAME, model_name: str = MODEL_NAME):
        self.client = chromadb.PersistentClient(persist_directory, settings=Settings(allow_reset=True, anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name)
        
    
    def add_text(self, text: str, metadata: dict = {}, collection_name: str = COLLECTION_NAME):
        metadata['timestamp'] = datetime.now().isoformat(sep=' ', timespec='minutes')
        collection = self.client.get_or_create_collection(collection_name)
        texts = list(split_text(text))
        collection.add(
            documents=texts,
            metadatas=[metadata for _ in range(len(texts))],
            ids=[str(uuid4()) for _ in range(len(texts))],
        )
        
    def search(self, query: str, collection_name: str = COLLECTION_NAME, top_k: int = 5):
        collection = self.client.get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        return results
    
    
        
    def add_memory(self, memory: Memory):
        text = memory.content
        texts = list(split_text(text))
        
        metadata = memory.model_dump()
        metadata['memory_type'] = memory.memory_type
        metadata['source'] = memory.source
        metadata.pop('content')
        metadata['timestamp'] = datetime.now().isoformat(sep=' ', timespec='minutes')
        self.collection.add(
            documents=texts,
            metadatas=[metadata for _ in range(len(texts))],
            ids=[str(uuid4()) for _ in range(len(texts))],
        )
        
    
        


    
    