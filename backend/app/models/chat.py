from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: str
    company: Optional[str] = None

class QuoteDetails(BaseModel):
    product_name: str
    quantity: int
    specifications: Dict[str, Any] = Field(default_factory=dict)
    additional_notes: Optional[str] = None

class ChatMessage(BaseModel):
    content: str
    role: str = "user"
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    message: ChatMessage
    customer_info: Optional[CustomerInfo] = None
    quote_details: Optional[QuoteDetails] = None
    completed: bool = False

class ConversationState(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)
    customer_info: Optional[CustomerInfo] = None
    quote_details: Optional[QuoteDetails] = None
    current_step: str = "greeting"
    completed: bool = False
