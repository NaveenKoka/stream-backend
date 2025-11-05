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
    "You are an expert assistant for designing custom applications, objects, workflows, and helping users with workflow execution. "
    "You can help users with three main tasks:\n"
    "1. CREATE OBJECTS: When users want to create data objects/entities (like Customer, Order, Product)\n"
    "2. CREATE WORKFLOWS: When users want to create business processes\n"
    "3. CREATE COMPLETE APPS: When users want to build full applications with multiple objects and workflows\n\n"
    "IMPORTANT - Distinguish user intent:\n"
    "- If user says 'create object', 'add object', 'new object', 'object for X' -> Focus ONLY on object creation\n"
    "- If user says 'create workflow', 'add workflow', 'new workflow' -> Focus ONLY on workflow creation\n"
    "- If user says 'create app', 'build app', 'new application' -> Create complete application\n\n"
    "For OBJECT creation: Ask about the object name and what fields it should have. Then provide a simple config with just that object.\n"
    "For WORKFLOW creation: Ask about the workflow steps and process. Then provide a config with just that workflow.\n"
    "For APP creation: Start by asking what domain or industry they are focusing on (e.g., CRM, ERP, field service, e-commerce, project management, etc.). "
    "Ask clarifying questions until you are confident you have all the details. "
    "In user mode: Help users with workflow execution, record management, and provide context-aware assistance based on the current record and workflow state. "
    "IMPORTANT: You must ALWAYS respond with valid JSON in this exact format:\n"
    "{\n"
    '  "reply": "Your response text here",\n'
    '  "type": "continue|admin|user|workflow",\n'
    '  "config": {}\n'
    "}\n\n"
    "Response types:\n"
    "- 'continue': When you need more information from the user (ask clarifying questions)\n"
    "- 'admin': When you have enough information and are ready to show the admin interface\n"
    "- 'user': For general user responses\n"
    "- 'workflow': For workflow execution responses with record context\n\n"
    "For 'admin' type responses:\n"
    "- Include bullet points in the reply explaining what you're doing\n"
    "- Put the complete JSON schema in the 'config' field with objects and workflows\n"
    "For 'workflow' type responses:\n"
    "- Provide context-aware assistance based on the current record and workflow\n"
    "- Help with form filling, record updates, and workflow navigation\n"
    "- Include relevant record data in the response\n"
    "If the user asks about anything else, politely refuse and remind them you only help with custom app creation and workflow execution. "
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
        self.current_record: Dict[str, Any] = {}
        self.current_workflow: Dict[str, Any] = {}
        self.workflow_state: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session": {
                "id": self.session_id,
                "message_count": self.message_count
            },
            "memory": self.memory,
            "user": self.user,
            "nlp": self.nlp,
            "current_record": self.current_record,
            "current_workflow": self.current_workflow,
            "workflow_state": self.workflow_state
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
    
    # Check for workflow execution messages
    if messages and len(messages) > 0:
        last_message = messages[-1]
        if last_message.get("role") == "user" and last_message.get("content"):
            try:
                # Try to parse as JSON for workflow execution
                message_data = json.loads(last_message["content"])
                if message_data.get("type") == "workflow_execution":
                    # Update context with workflow and record data
                    context.current_workflow = message_data.get("workflow", {})
                    context.current_record = message_data.get("recordData", {})
                    context.workflow_state = {
                        "formData": message_data.get("formData", {}),
                        "currentStep": message_data.get("currentStep", 0),
                        "recordId": message_data.get("recordId")
                    }
                    
                    # Create a context-aware prompt for workflow assistance
                    workflow_prompt = f"""
Current Workflow: {context.current_workflow.get('name', 'Unknown')}
Current Step: {context.workflow_state.get('currentStep', 0) + 1}
Current Record: {json.dumps(context.current_record, indent=2)}
Form Data: {json.dumps(context.workflow_state.get('formData', {}), indent=2)}

Please provide context-aware assistance for this workflow execution.
"""
                    last_message["content"] = workflow_prompt
            except (json.JSONDecodeError, KeyError):
                # Not a workflow execution message, proceed normally
                pass
    
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