from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class QuoteDetails(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = None
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
