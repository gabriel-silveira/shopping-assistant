from typing import List, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo
from ..services.retrive_products_data import retrieve_product_data
from ..prompts.prompts import ask_customer_name_prompt, company_name
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
    ) -> ConversationState:
        """Send assistant response to the customer."""

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

    def greeting(state: ConversationState) -> ConversationState:
        """Send initial greeting to the customer."""

        state.current_step = "greeting"

        state.messages.append(ChatMessage(
            content=f"Olá! Sou o assistente virtual da {company_name}. Como posso te ajudar?",
            role="assistant"
        ))

        return state

    def ask_customer_name(
        history: List[Union[HumanMessage, AIMessage]],
        state: ConversationState,
    ) -> ConversationState:
        state.current_step = "ask_customer_name"

        return assistant_response(ask_customer_name_prompt, history, state)
    
    def insist_customer_name(
        history: List[Union[HumanMessage, AIMessage]],
        state: ConversationState,
    ) -> ConversationState:
        state.current_step = "insist_customer_name"

        state.messages.append(ChatMessage(
            content=f"Caro cliente, para que possamos prosseguir com o atendimento. Por favor, informe seu nome completo.",
            role="assistant"
        ))

        return state
    
    def get_conversation_history(state: ConversationState) -> List[Union[HumanMessage, AIMessage]]:
        history: List[Union[HumanMessage, AIMessage]] = []

        for msg in state.messages:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))
        
        return history

    def process_state(state: ConversationState = None) -> ConversationState:
        """Process the conversation state and determine next steps."""

        # Ensure state is properly initialized
        if state is None:
            state = ConversationState.create_empty()

        # Send initial greeting to the customer
        if not state.messages:
            return greeting(state)

        # Convert chat history to LangChain message format
        history = get_conversation_history(state)

        # Ask customer name, before proceeding with conversation
        if len(state.messages) == 2 and state.messages[-1].role == "user":
            return ask_customer_name(history, state)

        # if we have the customer name
        if state.customer_info.name:
            return retrieve_product_data(state.messages[-1].content, history, state)
        else:
            # try to get customer name...

            name = extract_customer_name(state.messages[-1].content)

            print(f"Extracted name: {name}")

            # proceed answering the first customer question
            if name:
                print('HAS NAME')
                state.current_step = "customer_questions"

                state.customer_info.name = name

                print(f"Set customer name: {state.customer_info.name}")

                return retrieve_product_data(state.messages[-1].content, history, state)
            else:
                print('DOES NOT HAVE NAME')

                # ask customer name again!
                return insist_customer_name(history, state)

    return process_state
