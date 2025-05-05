from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

class CustomerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    content: str
    role: str = "user"
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    message: ChatMessage
    customer_info: Optional[CustomerInfo] = None
    quote_details: Optional[List[Dict]] = None
    completed: bool = False

class QuoteDetails(BaseModel):
    pass

class QuoteItemDetails(BaseModel):
    pass

class ConversationState(BaseModel):
    """Represents the state of a conversation."""
    model_config = ConfigDict(from_attributes=True)
    
    messages: List[ChatMessage] = Field(default_factory=list)
    customer_info: Optional[CustomerInfo] = None
    quote_details: Optional[QuoteDetails] = None
    current_step: str = Field(default="greeting")

    current_product: Optional[QuoteItemDetails] = None
    current_product_name: Optional[str] = None
    current_product_specifications: Optional[str] = None
    
    completed: bool = Field(default=False)

    @classmethod
    def create_empty(cls) -> 'ConversationState':
        """Create a new empty conversation state with initialized lists."""
        return cls(
            messages=[],
            current_step="greeting",
            completed=False
        )
