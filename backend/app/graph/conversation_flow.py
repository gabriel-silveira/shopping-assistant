from typing import List, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..models.chat import ConversationState, ChatMessage, CustomerInfo
from ..services.milvus_service import MilvusService
from ..examples.retrive_products_data import retrieve_product_data
from ..services.text_extractor import (
    extract_customer_name,
    extract_customer_email,
    extract_customer_phone,
    extract_customer_company,
    extract_quote_details,
)

company_name = "CSN"

def create_conversation_graph():
    def add_product(state: ConversationState):
        try:
            print("\nAdding current product to quote:")

            print(f"State quote details BEFORE: {state.quote_details}")
            
            # Create quote_details if it doesn't exist
            if state.quote_details is None and state.current_product != None:
                state.quote_details = [
                    {
                        "product_name": state.current_product["product_name"],
                        "quantity": 0,
                        "specifications": "",
                        "additional_notes": ""
                    }
                ]

                print(f"State quote details AFTER: {state.quote_details}")

                # reset current product
                state.current_product = None

        except Exception as e:
            print(f"Error adding product to quote: {e}")

    def assistant_response(
        system_template: str,
        history: List[Union[HumanMessage, AIMessage]],
        state: ConversationState,
        node_name: str,
    ) -> ConversationState:
        print(f"Node: {node_name}\n")

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
            
            # First question: Name
            system_template = """Agradeça o interesse do cliente e pergunte seu nome de forma educada.
            Não solicite nenhuma informação sobre produtos nesta etapa."""

            return assistant_response(system_template, history, state, "ask_name")

        # if we have customer name, collect more customer data
        if state.customer_info:
            # Extract each piece of information from last message
            name = extract_customer_name(state.messages[-1].content)
            email = extract_customer_email(state.messages[-1].content)
            phone = extract_customer_phone(state.messages[-1].content)
            company = extract_customer_company(state.messages[-1].content)

            # Extract company from last message (optional)
            # if company:
            #     state.customer_info.company = company

            # thank for the customer name, ask for quote / product details...
            if state.customer_info.name and name:
                details = extract_quote_details(state.messages[1].content)

                first_product_word = details.get('product_name').split(' ', 1)[0]

                if first_product_word:
                    print('Product name: ', first_product_word)

                    milvus_service = MilvusService()
                    product = milvus_service.search_similar_products(first_product_word)

                    if product and len(product) > 0:
                        # store the current product (to be added to the quote)
                        state.current_product = {
                            "id": product[0]['id'],
                            "product_name": product[0]['product_name'],
                            "quantity": 0,
                            "specifications": "",
                            "additional_notes": ""
                        }

                        print(f"Produto encontrado: {product[0]['id']}")
                    
                    return retrieve_product_data(first_product_word, history, state, "ask_product_0")
                else:
                    # Ask for product
                    system_template = f"""Agradeça o nome fornecido e cordialmente pergunte como pode ajudar?"""

                    return assistant_response(system_template, history, state, "ask_product_0")



            # ask for quote / product details...
            if state.customer_info.name:
                details = extract_quote_details(state.messages[-1].content)

                # add product to quotes
                if state.current_product and state.messages[-1].content == "Sim":
                    print('Adding product: ', state.current_product.get("product_name"))

                    # add product to quote
                    add_product(state)

                    system_template = """Você está coletando informações de produtos para o orçamento.
                    
                    REGRAS IMPORTANTES
                    - Se o usuário responder Sim, significa que ele quis adicionar o produto ao orçamento.
                    - Neste caso, pergunte cordialmente a quantidade desejada do produto."""
                    return assistant_response(system_template, history, state, "ask_add_product_to_quote")
                else:
                    # inform quantity
                    system_template = """Você está coletando informações de produtos para o orçamento.
                    
                    REGRAS IMPORTANTES
                    - Neste momento o cliente eestá informando a quantidade do produto adicionado ao orçamento.
                    - Agradeça e pergunte se o cliente deseja adicionar mais produtos ao orçamento ou se deseja finalizar o orçamento.
                    """
                    return assistant_response(system_template, history, state, "inform_quantity")

            
            # ask email
            if not state.customer_info.name and name:
                print('B')
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
            if (
                state.customer_info.name
                and state.customer_info.email
                and state.customer_info.phone
                and not state.customer_info.company
            ):
                print("Telefone fornecido: ", phone)

                state.customer_info.phone = phone

                # Ask for company (optional)
                system_template = """Agradeça o telefone fornecido e pergunte se o pedido é para alguma empresa, lembrando que esta informação não é obrigatória."""

                print("Template: ", system_template)

                return assistant_response(system_template, history, state, "ask_company")



            details = extract_quote_details(state.messages[-1].content)

            # If we have additional notes, update them (END)
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
            
            #elif state.quote_details and len(state.quote_details.items) == 0:
            #    system_template = """Sua responsabilidade é coletar informações para orçamentos.
            #    Pergunte qual produto da CSN o cliente deseja."""

            #    return assistant_response(system_template, history, state, "ask_missing_product")
            
            elif state.quote_details and not state.quote_details.quantity:
                system_template = """Sua responsabilidade é coletar informações para orçamentos.
                Pergunte a quantidade do produto."""

                return assistant_response(system_template, history, state, "ask_missing_quantity")
            
            elif state.quote_details and not state.quote_details.specifications:
                system_template = """Sua responsabilidade é coletar informações para orçamentos.
                Pergunte as especificações do produto."""

                return assistant_response(system_template, history, state, "ask_missing_specifications")

    return process_state
