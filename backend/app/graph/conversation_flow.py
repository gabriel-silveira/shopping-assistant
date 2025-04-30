from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo, QuoteDetails
import re

def extract_customer_info(text: str) -> Dict[str, str]:
    """Extract customer information from text using regex patterns."""
    info = {}
    
    # Name pattern - looks for common name introduction patterns
    name_patterns = [
        r"(?i)meu nome (?:é|e) ([^\n.,]+)",
        r"(?i)me chamo ([^\n.,]+)",
        r"(?i)sou (?:o|a) ([^\n.,]+)",
        # Se não encontrar nenhum padrão acima e o texto não contiver caracteres especiais
        # e tiver entre 2 e 50 caracteres, considera como nome
        r"^([A-Za-zÀ-ÖØ-öø-ÿ\s]{2,50})$"
    ]
    for pattern in name_patterns:
        if match := re.search(pattern, text.strip()):
            info['name'] = match.group(1).strip()
            break
    
    # Email pattern
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    if match := re.search(email_pattern, text):
        info['email'] = match.group(0)
    
    # Phone pattern - matches various formats
    phone_pattern = r'(?:\+?55\s?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[-\s]?\d{4}'
    if match := re.search(phone_pattern, text):
        info['phone'] = match.group(0)
    
    # Company pattern
    company_patterns = [
        r"(?i)(?:empresa|companhia|trabalho\s+(?:na|no|em)|da empresa) ([^\n.,]+)",
        r"(?i)(?:representando|represento) (?:a empresa )?([^\n.,]+)"
    ]
    for pattern in company_patterns:
        if match := re.search(pattern, text):
            info['company'] = match.group(1).strip()
            break
    
    return info

def extract_quote_details(text: str) -> Dict[str, Any]:
    """Extract quote details from text using regex patterns."""
    details = {}
    
    # Product name patterns
    product_patterns = [
        r"(?i)(?:quero|preciso|gostaria de) (?:comprar|pedir|orçar|encomendar) (?:um|uma|o|a|os|as)? ([^\n.,0-9]+)",
        r"(?i)(?:produto|item|peça|material): ?([^\n.,0-9]+)",
        r"(?i)(?:preciso|quero|gostaria) de (?:um|uma|o|a|os|as)? ([^\n.,0-9]+)"
    ]
    for pattern in product_patterns:
        if match := re.search(pattern, text):
            details['product_name'] = match.group(1).strip()
            break
    
    # Quantity patterns
    quantity_patterns = [
        r"(?i)(\d+) (?:unidades?|peças?|itens?)",
        r"(?i)quantidade:? ?(\d+)",
        r"(?i)(?:preciso|quero|gostaria) de (\d+)"
    ]
    for pattern in quantity_patterns:
        if match := re.search(pattern, text):
            details['quantity'] = int(match.group(1))
            break
    
    # Specifications patterns
    spec_patterns = [
        r"(?i)(?:especificações?|detalhes?|características?):? ?([^\n]+)",
        r"(?i)(?:medidas?|tamanhos?|dimensões?):? ?([^\n]+)",
        r"(?i)(?:cores?|materiais?):? ?([^\n]+)"
    ]
    for pattern in spec_patterns:
        if match := re.search(pattern, text):
            if 'specifications' not in details:
                details['specifications'] = {}
            details['specifications']['details'] = match.group(1).strip()
    
    # Additional notes patterns
    notes_patterns = [
        r"(?i)(?:observações?|notas?|comentários?):? ?([^\n]+)",
        r"(?i)(?:importante|obs):? ?([^\n]+)"
    ]
    for pattern in notes_patterns:
        if match := re.search(pattern, text):
            details['additional_notes'] = match.group(1).strip()
            break
    
    return details

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
                # Try to extract customer info from user messages
                info = extract_customer_info(msg.content)
                if info:
                    # Update customer info
                    current_info = {}
                    if state.customer_info:
                        current_info = state.customer_info.dict()
                    current_info.update(info)
                    
                    # Atualiza o CustomerInfo com as informações parciais
                    state.customer_info = CustomerInfo(**current_info)
                    print("Updated customer info:", state.customer_info)
                
                # Try to extract quote details from user messages
                if state.customer_info and any([
                    getattr(state.customer_info, field, None)
                    for field in ['name', 'email', 'phone']
                ]):
                    details = extract_quote_details(msg.content)
                    if details:
                        # Update quote details
                        current_details = {}
                        if state.quote_details:
                            current_details = state.quote_details.dict()
                        current_details.update(details)
                        
                        # Atualiza o QuoteDetails com as informações parciais
                        state.quote_details = QuoteDetails(**current_details)
                        print("Updated quote details:", state.quote_details)

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
