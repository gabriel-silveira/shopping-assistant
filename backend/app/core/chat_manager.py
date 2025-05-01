from typing import Dict
from ..models.chat import ConversationState, ChatMessage, ChatResponse
from ..graph.conversation_flow import create_conversation_graph

class ChatManager:
    def __init__(self):
        self.state = ConversationState()
        self.workflow = create_conversation_graph()

    def process_message(self, message: ChatMessage) -> ChatResponse:
        print("Processing message:", message)

        # Add user message to state
        if message: self.state.messages.append(message)
        
        print("Self workflow:", self.workflow)
        # Process through workflow
        self.state = self.workflow(self.state)
        print("Self state:", self.state)
        
        # Get last assistant message
        last_message = next(
            (msg for msg in reversed(self.state.messages) if msg.role == "assistant"),
            None
        )
        
        if not last_message:
            raise ValueError("No assistant message found in state")
        
        # Create response
        return ChatResponse(
            message=last_message,
            customer_info=self.state.customer_info,
            quote_details=self.state.quote_details,
            completed=self.state.completed
        )
