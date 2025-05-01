from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class QuoteDetails(BaseModel):
    """Details of a quote request."""
    product_name: str = ""
    quantity: int = 0
    specifications: str = ""
    additional_notes: str = ""

    @classmethod
    def create_empty(cls) -> 'QuoteDetails':
        """Create an empty QuoteDetails with default values."""
        return cls(
            product_name="",
            quantity=0,
            specifications="",
            additional_notes=""
        )

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to ensure all fields have default values."""
        data = super().dict(*args, **kwargs)
        # Ensure all fields have default values
        data["product_name"] = data.get("product_name", "") or ""
        data["quantity"] = data.get("quantity", 0) or 0
        data["specifications"] = data.get("specifications", "") or ""
        data["additional_notes"] = data.get("additional_notes", "") or ""
        return data

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
