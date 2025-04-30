from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo, QuoteDetails

def create_conversation_graph():
    def process_state(state: ConversationState) -> ConversationState:
        if not state.messages:
            # Initial greeting
            response = ChatMessage(
                content="Olá! Sou o assistente de orçamentos. Como posso ajudar você hoje?",
                role="assistant"
            )
            state.messages.append(response)
            return state

        # Initialize LLM
        llm = ChatOpenAI(temperature=0.7)
        
        # Convert chat history to LangChain message format
        history = []
        for msg in state.messages:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))

        # Process based on current state
        if not state.customer_info or not all([
            getattr(state.customer_info, field, None)
            for field in ['name', 'email', 'phone']
        ]):
            print('Collecting customer information')
            
            # Collecting customer information
            system_template = """Você é um assistente profissional coletando informações para um orçamento.
            Colete de forma natural as seguintes informações do cliente:
            - Nome
            - Email
            - Telefone
            - Empresa (opcional)
            
            Se já tiver todas as informações obrigatórias, confirme com o cliente e prossiga para coletar os detalhes do pedido."""

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                MessagesPlaceholder(variable_name="history")
            ])
            
            # Create chain
            chain = prompt | llm
            
            # Run chain
            ai_response = chain.invoke({"history": history})
            
            # Add response to state
            state.messages.append(ChatMessage(
                content=ai_response.content,
                role="assistant"
            ))

        elif not state.quote_details or not all([
            getattr(state.quote_details, field, None)
            for field in ['product_name', 'quantity']
        ]):
            print('Collecting quote details')

            # Collecting quote details
            system_template = """Você é um assistente profissional coletando informações para um orçamento.
            Colete de forma natural as seguintes informações do pedido:
            - Nome do produto
            - Quantidade
            - Especificações específicas
            - Observações adicionais (opcional)
            
            Se já tiver todas as informações necessárias, faça um resumo do pedido e pergunte se está tudo correto."""

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                MessagesPlaceholder(variable_name="history")
            ])
            
            # Create chain
            chain = prompt | llm
            
            # Run chain
            ai_response = chain.invoke({"history": history})
            
            # Add response to state
            state.messages.append(ChatMessage(
                content=ai_response.content,
                role="assistant"
            ))

        else:
            print('Finalizing conversation')

            # Finalizing conversation
            system_template = """Faça um resumo completo do pedido de orçamento e agradeça ao cliente."""
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                MessagesPlaceholder(variable_name="history")
            ])
            
            # Create chain
            chain = prompt | llm
            
            # Run chain
            ai_response = chain.invoke({"history": history})
            
            # Add response to state
            state.messages.append(ChatMessage(
                content=ai_response.content,
                role="assistant"
            ))
            state.completed = True

        return state
    
    return process_state
