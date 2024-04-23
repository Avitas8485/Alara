# Alara - AI Assistant Agent

Alara is an AI assistant that helps people with their daily tasks with more emphasis on AI part, at least thats the end goal, to make it more than a simple Assistant.

It is built using various components and frameworks, including:

1. **Speech-to-Text (STT)**: The agent uses the Whisper STT library for speech recognition.
2. **Wake Word Detection**: The agent uses a wake word detection module to detect when the user is addressing it.
3. **Intent Recognition**: The agent uses an Intent Recognition module to understand the user's intent
4. **Skill Manager**: The agent uses a Skill Manager to dynamically load and manage skills. Skills are plugins that allow the agent to perform tasks beyond the basic functionality.
5. **Text-to-Speech (TTS)**: The agent uses the Piper TTS library for speech synthesis.
6. **Large Language Model (LLM)**: The agent uses the LLaMa Chat Completion module for natural language processing and generation.
10. **Scheduler**: The agent uses a Scheduler Manager to schedule tasks and events.
11. **Automation Handler**: The agent uses an Automation Handler to handle automation workflows, including triggers, conditions, and actions.
12. **State Machine**: The agent uses a State Machine to manage the state of entities, such as agents and devices.
13. **Event Bus**: The agent uses an Event Bus to handle events and communication between components.

The agent's main functionality is to listen for user prompts, process them using the various components, and execute the appropriate skills to respond to the user's requests. The agent also has the ability to handle automation workflows, such as scheduling tasks and responding to events.

The agent is designed to be extensible and customizable, with the ability to add new skills and integrate with various devices and services.

### Components
Alara is composed of the following main components:

1. **Agent**: The main entry point for the agent, responsible for managing the various components and handling user input.
2. **Skill Manager**: Responsible for loading and managing skills, which are plugins that extend the agent's functionality.
3. **Automation Handler**: Responsible for handling automation workflows, including triggers, conditions, and actions.
4. **Tools and Toolkit**: Responsible for managing internal components (tools) and their dependencies.
5. **Integrations**: Responsible for integrating with external devices and services.

### Usage

To use the Alara agent, you can run the `main.py` script. The agent will start listening for user input and respond accordingly.

### Roadmap
- Make the setup process more user friendly (currently, most components need to be set up and installed beforehand)
- Implement more skills and integrations
- Improve the automation workflow
- Enhance the natural language processing capabilities
- Improve the overall reliability and robustness of the system
- Add agent Actions.

### Contributing
If you'd like to contribute to the Alara project, please feel free to submit a pull request or open an issue on the project's GitHub repository. 

Go easy on me, I don't know what I'm doing

