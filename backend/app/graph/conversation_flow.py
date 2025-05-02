from typing import List, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo, QuoteDetails
from ..services.text_extractor import (
    extract_customer_name,
    extract_customer_email,
    extract_customer_phone,
    extract_customer_company,
)

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
                current_info = {}
                if state.customer_info:
                    current_info = state.customer_info.dict()
                
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
            
            # First question: Name
            system_template = """Agradeça o interesse do cliente e pergunte seu nome de forma educada.
            Não solicite nenhuma informação sobre produtos nesta etapa."""

            return assistant_response(system_template, history, state, "ask_name")

        # Check if we have customer name and need to collect more
        if state.customer_info:
            print("Message content:")
            print(f"{state.messages[-1].content}\n")

            # Extract each piece of information from last message
            name = extract_customer_name(state.messages[-1].content)
            email = extract_customer_email(state.messages[-1].content)
            phone = extract_customer_phone(state.messages[-1].content)
            company = extract_customer_company(state.messages[-1].content)

            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Phone: {phone}")
            print(f"Company: {company}\n")
            
            # ask email
            if not state.customer_info.name and name:
                state.customer_info.name = name
                # Ask for email
                system_template = """Agradeça o nome fornecido e solicite o e-mail do cliente para envio do orçamento."""

                return assistant_response(system_template, history, state, "ask_email")

            # ask phone
            if not state.customer_info.email and email:
                state.customer_info.email = email
                # Ask for phone
                system_template = """Agradeça o e-mail fornecido e solicite um número de telefone para contato."""

                return assistant_response(system_template, history, state, "ask_phone")

            # ask company
            if not state.customer_info.company and phone:
                state.customer_info.phone = phone

                # Ask for company (optional)
                system_template = """Agradeça o telefone fornecido e pergunte se o pedido é para alguma empresa e, se sim, solicite o nome da empresa."""

                return assistant_response(system_template, history, state, "ask_company")

            # After collecting customer info, start collecting quote details
            if not state.quote_details and state.customer_info.name and state.customer_info.email and state.customer_info.phone:
                # Initialize quote details
                state.quote_details = QuoteDetails.create_empty()

                # Extract company from last message (optional)
                if company:
                    state.customer_info.company = company

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
