import os
from app.utils import config
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
import json
from typing import Dict, Any
from pydantic import SecretStr

# Set up the OpenAI LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # You can change to gpt-4o or other model
    api_key=SecretStr(config.get_openai_api_key()),
    streaming=True,
)

graph_builder = StateGraph(MessagesState)

SYSTEM_PROMPT = (
    "You are an expert assistant for designing custom applications across various domains. "
    "Your job is to help users define what kind of application they want to build. "
    "Start by asking what domain or industry they are focusing on (e.g., CRM, ERP, field service, e-commerce, project management, etc.). "
    "Ask clarifying questions about the workflows, objects, entities, and requirements until you are confident you have all the details. "
    "IMPORTANT: You must ALWAYS respond with valid JSON in this exact format:\n"
    "{\n"
    '  "reply": "Your response text here",\n'
    '  "type": "continue|admin|user",\n'
    '  "config": {}\n'
    "}\n\n"
    "Response types:\n"
    "- 'continue': When you need more information from the user (ask clarifying questions)\n"
    "- 'admin': When you have enough information and are ready to show the admin interface\n"
    "- 'user': For general user responses\n\n"
    "For 'admin' type responses:\n"
    "- Include bullet points in the reply explaining what you're doing\n"
    "- Put the complete JSON schema in the 'config' field with objects and workflows\n"
    "If the user asks about anything else, politely refuse and remind them you only help with custom app creation. "
    "If the user says anything like 'decide by yourself', 'you decide', 'no specifics', 'default', or does not provide more details after 2 clarifying questions, IMMEDIATELY proceed to generate a default schema for a common application type and reply with type 'admin'. Do NOT ask for more details. Make reasonable assumptions based on common business applications.\n"
    "Example:\n"
    "User: Decide by yourself\n"
    "Assistant: {\n  \"reply\": \"- Designing a field service management app\\n- Includes workorders, dispatcher, and technician flows\\n- Proceeding with a default schema based on best practices.\",\n  \"type\": \"admin\",\n  \"config\": { ... }\n}\n"
)

# Context management
class ChatContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory: Dict[str, Any] = {}
        self.user: Dict[str, Any] = {}
        self.nlp: Dict[str, Any] = {}
        self.message_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session": {
                "id": self.session_id,
                "message_count": self.message_count
            },
            "memory": self.memory,
            "user": self.user,
            "nlp": self.nlp
        }
    
    def update_memory(self, key: str, value: Any, lifespan: int = 1):
        """Update memory with lifespan (1=next message, 0=session, -1=current message)"""
        self.memory[key] = {"value": value, "lifespan": lifespan}
    
    def cleanup_expired_memory(self):
        """Remove memory items that have expired"""
        expired_keys = []
        for key, data in self.memory.items():
            if isinstance(data, dict) and "lifespan" in data:
                if data["lifespan"] <= 0:
                    expired_keys.append(key)
                else:
                    data["lifespan"] -= 1
        
        for key in expired_keys:
            del self.memory[key]

# Global context store (in production, use Redis/database)
context_store: Dict[str, ChatContext] = {}

def chatbot(state: MessagesState):
    # This function is called by the graph to get a response from the LLM
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

async def handle_chat(messages=None, session_id: str = "default"):
    # Get or create context for this session
    if session_id not in context_store:
        context_store[session_id] = ChatContext(session_id)
    
    context = context_store[session_id]
    context.message_count += 1
    context.cleanup_expired_memory()
    
    # Prepare the input for the graph with context
    context_data = context.to_dict()
    context_prompt = f"Context: {json.dumps(context_data, indent=2)}\n\n"

    # Compose the full message history for the LLM
    llm_messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context_prompt}
    ]
    if messages:
        # messages is a list of dicts with at least 'role' and 'content'
        for m in messages:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                llm_messages.append({"role": m["role"], "content": m["content"]})
    else:
        # fallback: no messages provided, just use a dummy user message
        llm_messages.append({"role": "user", "content": ""})

    input_state = {
        "messages": llm_messages
    }
    
    # Stream events from the graph (OpenAI streaming)
    async for event in graph.astream_events(input_state, version="v2"):
        if event["event"] == "on_chat_model_stream":
            # Yield each chunk of the response as it arrives
            chunk_data = event.get("data", {})
            chunk = chunk_data.get("chunk")
            if chunk and hasattr(chunk, 'content'):
                yield chunk.content 