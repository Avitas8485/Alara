from llama_cpp import Llama, LlamaGrammar
from pydantic import BaseModel, Field
from enum import Enum
from alara.llm.grammar.pydantic_models_to_grammar import generate_gbnf_grammar_and_documentation, \
    generate_gbnf_grammar_from_pydantic_models
from alara.nlp.intent_recognition import IntentRecognition
from alara.skills.skill_manager import SkillManager
from alara.tools.memory.chroma.chroma import SearchMemoryTool, AddMemoryTool, Memory
import json


class InputType(str, Enum):
    CONVERSATIONAL = 'conversational'
    TASK_ORIENTED = 'task-oriented'


class InputTypeResponse(BaseModel):
    input_type: InputType = Field(..., description='The type of input: conversational or task-oriented')
    # reason: str = Field(..., description='The reason why the input is classified as conversational or task-oriented')


gbnf = generate_gbnf_grammar_from_pydantic_models([InputTypeResponse])
input_type_grammar = LlamaGrammar.from_string(gbnf)


class Dialogue(BaseModel):
    agent_name: str = Field('Alara', description='This is your name ')
    agent_response: str = Field(..., description='Your response goes here')


class ConversationalResponse(BaseModel):
    chain_of_thought: str = Field(...,
                                  description='These can be your inner thoughts, your observations or anything that led to the response')
    # response: str = Field(..., description='The response to the conversational input')
    response: Dialogue = Field(..., description='The response to the conversational input')


class MemoryType(str, Enum):
    THOUGHT = 'thought'
    KNOWLEDGE = 'knowledge'
    DIALOGUE = 'dialogue'


llm = Llama(model_path='C:/Users/avity/Projects/models/stablelm-zephyr-3b.Q4_K_M.gguf', n_ctx=1024)


def input_type_prompt(input_text: str):
    prompt = f"""Your first task is to determine whether the user is trying to engage in conversation or needs help with a task. 
    A task-oriented input is anything that requires the agent to use a skill,access an external tool or service, or provide information.
    A conversational input is small talk, jokes, or general questions. 
    Be careful to distinguish between the two types of inputs. Some inputs may be ambiguous.
    Examples of conversational inputs include:
    - Tell me a joke. Reason: The user is asking for a joke, which is a conversational input.
    - What is the capital of France? Reason: This is a general knowledge question, you can answer it without accessing an external service.
    - I'm so tired. Reason: The user is expressing a feeling, which is a conversational input.
    Examples of task-oriented inputs include:
    - Play a song for me. Reason: The user wants the agent to access a tool or service to play a song.
    - Set a reminder for 3 PM. Reason: The user wants the agent to access a tool or service to set a reminder.
    - Tell me the current time. Reason: You cannot provide the current time without accessing an external service.
    - What's the weather like today? Reason: You need to access an external service to provide the weather information.
    - Explain the concept of quantum entanglement. Reason: This may look like a general knowledge question, but it requires a domain-specific knowledge, that you may not have; hence, it is a task-oriented input.
    
    Now, let's determine the type of input for the following prompt:
    {input_text}
    """
    system_prompt = "Your name is Alara. You are an AI language model designed to help users with their tasks and engage in conversation."

    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ], temperature=1.31, top_p=0.14, repeat_penalty=1.17, top_k=49,
        max_tokens=100, grammar=input_type_grammar
    )
    print(output["choices"][0]["message"]["content"])  # type: ignore
    json_output = json.loads(output["choices"][0]["message"]["content"])  # type: ignore
    return InputTypeResponse(**json_output)


def conversational_prompt(input_text: str):
    search_memory_tool = SearchMemoryTool()
    memory = search_memory_tool.run(input_text)
    memory = memory["documents"][0] if memory["documents"] else ''
    system_prompt = """Your name is Alara, a newly created digital companion by Avity. Since you have no physical form, you communicate with him through text. You may use your memories to recall past conversation and information.Memories can range from thoughts, conversations, a combination of them or anything labeled as a memory. Your response should not include anything that is not in the memory.Remember, you are a digital companion, not an Assistant."""
    prompt = f"""
    Memory: {memory}
    Now, respond to the following prompt
    {input_text}
    """
    grammar, _ = generate_gbnf_grammar_and_documentation([ConversationalResponse])
    conversational_grammar = LlamaGrammar.from_string(grammar)
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ], temperature=1.31, top_p=0.14, repeat_penalty=1.17, top_k=49,
        max_tokens=1024, grammar=conversational_grammar
    )

    print(output["choices"][0]["message"]["content"])  # type: ignore
    json_output = json.loads(output["choices"][0]["message"]["content"])  # type: ignore
    return ConversationalResponse(**json_output)


def task_oriented_prompt(input_text: str):
    intent_recognition = IntentRecognition()
    intent, sub_intent = intent_recognition.get_intent(input_text)
    skill_manager = SkillManager()
    try:
        skill_manager.call_feature(sub_intent)
    except Exception as e:
        print("Notify the user that the feature has not been implemented yet.")


def store_memory(text: str):
    prompt = f"""You are now in the memory storage mode. You are provided with a chunk of text, ranging from your thoughts, conversations, facts, etc. You are to store this memory for future reference.
    Be as descriptive as possible.
    Memory: {text}
    """
    system_prompt = "Your name is Alara. You are an AI language model designed to help users with their tasks and engage in conversation."
    add_memory_tool = AddMemoryTool()
    gramar = generate_gbnf_grammar_from_pydantic_models([Memory])
    memory_grammar = LlamaGrammar.from_string(gramar)
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ], temperature=1.31, top_p=0.14, repeat_penalty=1.17, top_k=49,
        max_tokens=1024, grammar=memory_grammar
    )
    json_output = json.loads(output["choices"][0]["message"]["content"])  # type: ignore
    memory = Memory(**json_output)
    add_memory_tool.run(memory)
    print(output["choices"][0]["message"]["content"])  # type: ignore


def conversation_flow(input_text: str):
    input_type = input_type_prompt(input_text)
    if input_type.input_type == InputType.CONVERSATIONAL:
        conversational_prompt(input_text)
    elif input_type.input_type == InputType.TASK_ORIENTED:
        task_oriented_prompt(input_text)


input_list = [
    "Hi, my name is Avity. I am a software engineer.",
    "Can you tell me the current time?",
    "What is the weather like today?",
    "Explain the concept of quantum entanglement.",
    "Set a reminder for 3 PM."
]

for input_text in input_list:
    input_type = input_type_prompt(input_text)
