# Conversational Agent with Context Awareness

Aim: Creating a conversational agent that maintains context across multiple interactions

- implementing a conversational agent that can remember and refer to previous parts of the conversation, enhancing the overall interaction quality.

## High level overview

1. Set up enviroment: The foundation of  conversational agent
2. Chat history: Implement a system to manage multiple conversation sessions. Each session should be uniquely identifiable and associated with its own message history.
3. Conversation structure: create template that includes A system message defining the AI's role; A placeholder for conversation history, User Input
4. Conversational Chain: Combine the prompt template with the language model to create a basic conversational chain.

##process:

1. Set up Virtual enviroment ```python -m venv agent_env``` then ```agent_env\Scripts\activate```
2. Install needed packages insall ```pip install -q langchain langchain_experimental openai python-dotenv langchain_openai```