from typing import List, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo
from ..services.retrive_products_data import retrieve_product_data
from ..prompts.prompts import first_prompt, company_name
from ..services.text_extractor import (
    extract_customer_name,
    extract_customer_email,
    extract_customer_phone,
    extract_customer_company,
)

def create_conversation_graph():
    def assistant_response(
        system_template: str,
        history: List[Union[HumanMessage, AIMessage]],
        state: ConversationState,
        node_name: str,
    ) -> ConversationState:
        print(f"Node: {node_name}\n")

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="history")
        ])

        chain = prompt | ChatOpenAI(temperature=0.7)

        ai_response = chain.invoke({"history": history})

        state.messages.append(ChatMessage(
            content=ai_response.content,
            role="assistant"
        ))

        return state

    def process_state(state: ConversationState = None) -> ConversationState:
        """Process the conversation state and determine next steps."""
        # Ensure state is properly initialized
        if state is None:
            state = ConversationState.create_empty()

        if not state.messages:
            # Initial greeting
            state.messages.append(ChatMessage(
                content=f"Olá! Sou o assistente virtual da {company_name}. Como posso te ajudar?",
                role="assistant"
            ))
            return state

        # Convert chat history to LangChain message format
        history: List[Union[HumanMessage, AIMessage]] = []
        for msg in state.messages:
            if msg.role == "user":
                # Try to extract customer info from user messages
                current_info = {}
                if state.customer_info:
                    current_info = state.customer_info.model_dump()
                
                # Extract each piece of information
                name = extract_customer_name(msg.content)
                email = extract_customer_email(msg.content)
                phone = extract_customer_phone(msg.content)
                company = extract_customer_company(msg.content)
                
                # Update only the fields that were found
                if name:
                    current_info['name'] = name
                if email:
                    current_info['email'] = email
                if phone:
                    current_info['phone'] = phone
                if company:
                    current_info['company'] = company
                
                if any([name, email, phone, company]):
                    state.customer_info = CustomerInfo(**current_info)

                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))

        # ask name
        if len(state.messages) == 2 and state.messages[-1].role == "user":
            # After first user message, start collecting info
            
            # Initialize customer info
            state.customer_info = CustomerInfo()

            return assistant_response(first_prompt, history, state, "ask_name")

        # if we have customer name, collect more customer data
        if state.customer_info:
            # Extract each piece of information from last message
            # name = extract_customer_name(state.messages[-1].content)
            # email = extract_customer_email(state.messages[-1].content)
            # phone = extract_customer_phone(state.messages[-1].content)
            # company = extract_customer_company(state.messages[-1].content)

            return retrieve_product_data(state.messages[-1].content, history, state)

    return process_state
