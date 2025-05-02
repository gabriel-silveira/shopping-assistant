from typing import Dict, Any, List, Union
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
        r"(?i)(?:quero|preciso|gostaria|necessito)(?:\s+de)?\s+([^.,]+)",
        r"(?i)produto:?\s+([^.,]+)",
        r"(?i)item:?\s+([^.,]+)",
        r"(?i)pedido:?\s+([^.,]+)"
    ]
    for pattern in product_patterns:
        if match := re.search(pattern, text):
            details['product_name'] = match.group(1).strip()
            break
    
    # Quantity patterns
    quantity_patterns = [
        r"(?i)(\d+)\s+(?:unidades?|peças?|itens?|produtos?)",
        r"(?i)quantidade:?\s*(\d+)",
        r"(?i)(?:quero|preciso|gostaria|necessito)(?:\s+de)?\s+(\d+)",
        r"(\d+)\s*(?:un|pc|pç)"
    ]
    for pattern in quantity_patterns:
        if match := re.search(pattern, text):
            details['quantity'] = int(match.group(1))
            break
    
    # Specifications patterns
    spec_patterns = [
        r"(?i)(?:com|de)\s+(\d+\s*(?:mm|cm|m|pol|polegadas?))",
        r"(?i)especificações?:?\s+([^.]+)",
        r"(?i)(?:tamanho|medida|dimensão|diâmetro):?\s+([^.,]+)",
        r"(?i)material:?\s+([^.,]+)",
        r"(?i)(?:em|no)?\s*(?:tamanho|medida|dimensão|diâmetro)\s+(?:de\s+)?(\d+\s*(?:mm|cm|m|pol|polegadas?))",
        r"(?i)(?:de\s+)?(\d+\s*(?:mm|cm|m|pol|polegadas?))\s+(?:de\s+)?(?:tamanho|medida|dimensão|diâmetro)"
    ]
    for pattern in spec_patterns:
        if match := re.search(pattern, text):
            details['specifications'] = match.group(1).strip()
            break
    
    # Additional notes patterns
    note_patterns = [
        r"(?i)obs(?:ervações?)?:?\s+([^.]+)",
        r"(?i)notas?:?\s+([^.]+)",
        r"(?i)adicionais?:?\s+([^.]+)",
        r"(?i)também\s+(?:quero|preciso|gostaria)\s+([^.]+)"
    ]
    for pattern in note_patterns:
        if match := re.search(pattern, text):
            details['additional_notes'] = match.group(1).strip()
            break
    
    return details

company_name = "CSN"

def create_conversation_graph():
    def assistant_response(
        system_template: str,
        history: List[Union[HumanMessage, AIMessage]],
        state: ConversationState,
        node_name: str,
    ) -> ConversationState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"Você é o assistente virtual da {company_name}. {system_template}"),
            MessagesPlaceholder(variable_name="history")
        ])
        chain = prompt | ChatOpenAI(temperature=0.7)
        ai_response = chain.invoke({"history": history})
        state.messages.append(ChatMessage(
            content=ai_response.content,
            role="assistant"
        ))

        print(f"Node: {node_name}\n")

        return state

    def process_state(state: ConversationState) -> ConversationState:
        if not state.messages:
            # Initial greeting
            state.messages.append(ChatMessage(
                content=f"Olá! Sou o assistente virtual da {company_name}. Que tipo de produto você precisa e para qual finalidade?",
                role="assistant"
            ))
            return state

        # Convert chat history to LangChain message format
        history: List[Union[HumanMessage, AIMessage]] = []
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
                    state.customer_info = CustomerInfo(**current_info)

                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))

        # ask name
        if len(state.messages) == 2 and state.messages[-1].role == "user":
            # After first user message, start collecting info
            
            # Initialize customer info
            state.customer_info = CustomerInfo()
            
            # First question: Name
            system_template = """Agradeça o interesse do cliente e pergunte seu nome de forma educada.
            Não solicite nenhuma informação sobre produtos nesta etapa."""

            return assistant_response(system_template, history, state, "ask_name")

        # Check if we have customer name and need to collect more
        if state.customer_info:
            # Extract info from last message
            info = extract_customer_info(state.messages[-1].content)
            
            # ask email
            if not state.customer_info.name and info and info.get('name'):
                state.customer_info.name = info['name']
                # Ask for email
                system_template = """Agradeça o nome fornecido e solicite o e-mail do cliente para envio do orçamento."""

                return assistant_response(system_template, history, state, "ask_email")

            # ask phone
            if not state.customer_info.email and info and info.get('email'):
                state.customer_info.email = info['email']
                # Ask for phone
                system_template = """Agradeça o e-mail fornecido e solicite um número de telefone para contato."""

                return assistant_response(system_template, history, state, "ask_phone")

            # ask company
            if info and state.customer_info.phone and info.get('phone'):
                state.customer_info.phone = info.get('phone')
                # Ask for company (optional)
                system_template = """Agradeça o telefone fornecido e pergunte se o pedido é para alguma empresa e, se sim, solicite o nome da empresa."""

                return assistant_response(system_template, history, state, "ask_company")

            # After collecting customer info, start collecting quote details
            if not state.quote_details and state.customer_info.name and state.customer_info.email and state.customer_info.phone:
                # Initialize quote details
                state.quote_details = QuoteDetails.create_empty()

                # Extract company from last message (optional)
                if info and info.get('company'):
                    state.customer_info.company = info['company']

                # Ask for product
                system_template = """Se o cliente forneceu o nome da empresa, agradeça.
                Em seguida, pergunte qual produto da CSN o cliente deseja solicitar."""

                return assistant_response(system_template, history, state, "ask_product")

            # If we have additional notes, update them
            if state.quote_details and details.get('additional_notes'):
                state.quote_details.additional_notes = details['additional_notes']
                # Thank the client and finish
                system_template = """Agradeça o cliente e informe que em breve entraremos em contato com o orçamento."""

                return assistant_response(system_template, history, state, "finish")

            # If we haven't returned yet, ask for missing info
            if not state.customer_info.name:
                system_template = """Nesta etapa você precisa coletar o nome do cliente.
                Solicite educadamente o nome do cliente."""

                return assistant_response(system_template, history, state, "ask_missing_name")
            
            elif not state.customer_info.email:
                system_template = """Nesta etapa você precisa coletar o e-mail do cliente.
                Solicite educadamente o e-mail do cliente."""

                return assistant_response(system_template, history, state, "ask_missing_email")
            
            elif not state.customer_info.phone:
                system_template = """Nesta etapa você precisa coletar o número do telefone do cliente.
                Solicite educadamente o número de telefone do cliente."""

                return assistant_response(system_template, history, state, "ask_missing_phone")
            
            elif state.quote_details and not state.quote_details.product_name:
                system_template = """Sua responsabilidade é coletar informações para orçamentos.
                Pergunte qual produto da CSN o cliente deseja."""

                return assistant_response(system_template, history, state, "ask_missing_product")
            
            elif state.quote_details and not state.quote_details.quantity:
                system_template = """Sua responsabilidade é coletar informações para orçamentos.
                Pergunte a quantidade do produto."""

                return assistant_response(system_template, history, state, "ask_missing_quantity")
            
            elif state.quote_details and not state.quote_details.specifications:
                system_template = """Sua responsabilidade é coletar informações para orçamentos.
                Pergunte as especificações do produto."""

                return assistant_response(system_template, history, state, "ask_missing_specifications")

    return process_state
