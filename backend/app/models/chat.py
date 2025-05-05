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

class ConversationState(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    messages: List[ChatMessage] = Field(default_factory=list)
    customer_info: Optional[CustomerInfo] = None
    quote_details: Optional[List[Dict]] = None
    current_step: str = "greeting"
    current_product: Optional[Dict] = None
    completed: bool = False
