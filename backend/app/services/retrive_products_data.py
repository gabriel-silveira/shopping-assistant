from warnings import filterwarnings

# Supress specific warnings
filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")
filterwarnings("ignore", category=DeprecationWarning, module="langchain")

from typing import List, Union, Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from app.models.chat import ConversationState, ChatMessage
from app.prompts.prompts import main_prompt 
from app.services.text_extractor import extract_intention
from app.services.markdown_search_service import MarkdownSearchService

# Add project root to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def search_products(query: str) -> Union[str, List[Dict]]:
    """Útil para buscar informações sobre produtos disponíveis no catálogo da loja.
    Use esta ferramenta quando o usuário perguntar sobre produtos específicos, preços, descrições ou estoque.
    A ferramenta busca por palavras-chave no nome, categoria e descrição dos produtos."""
    
    print(f"\nBuscando por: {query}")
    
    # Inicializa o serviço de busca
    search_service = MarkdownSearchService()
    
    # Busca produtos
    results = search_service.search_products(query)
    
    if not results:
        return "Desculpe, não encontrei produtos correspondentes à sua busca. Poderia especificar melhor o tipo de produto que procura?"
    
    # Formata resposta
    response = ["Encontrei os seguintes produtos que podem te interessar:"]
    for product in results:
        product_info = [
            f"**{product['product_name']}**",
            f"Preço: R$ {product['price']:.2f}",
            f"Categoria: {product['category']}",
            f"Descrição: {product['description'][:200]}..."  # Limita tamanho da descrição
        ]
        response.append("\n".join(product_info))
    
    return "\n\n".join(response)


def retrieve_product_data(
    query: str,
    history: List[Union[HumanMessage, AIMessage]],
    state: ConversationState
) -> ConversationState:
    # Configuração do modelo de linguagem
    llm = ChatOpenAI(temperature=0.7)

    # Configuração das ferramentas disponíveis
    tools = [
        Tool(
            name="SearchProducts",  # Novo nome para a ferramenta
            func=search_products,   # Nova função de busca
            description=search_products.__doc__  # Nova descrição
        )
    ]

    # Template do prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", main_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Criação do agente
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    query_extracted = extract_intention(query)

    print(f"Query extracted: {query_extracted}\n")

    # Processa a entrada do usuário
    result = agent_executor.invoke({
        "input": query_extracted,
        "chat_history": history,
    })

    state.messages.append(ChatMessage(
        content=result["output"],
        role="assistant"
    ))
  
    return state