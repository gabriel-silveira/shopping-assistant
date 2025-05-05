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

# Add project root to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.milvus_service import MilvusService


def query_product_database(query: str) -> Union[str, List[Dict]]:
    """Útil para buscar informações sobre produtos disponíveis no banco de dados da loja. 
    Use esta ferramenta quando o usuário perguntar sobre produtos específicos, preços, descrições ou estoque. 
    A entrada para esta ferramenta deve ser o nome do produto ou palavras-chave relevantes para a busca."""
    
    # Normalize query (remove accents and convert to lowercase)
    import unicodedata
    query_normalized = unicodedata.normalize('NFKD', query.lower()) \
        .encode('ASCII', 'ignore') \
        .decode('ASCII')

    print(f"\nSearching for: {query_normalized}")
    
    milvus_service = MilvusService()
    results = milvus_service.search_similar_products(query_normalized)
    
    if not results:
        return "Desculpe, não encontrei nenhum produto com essas características. Poderia fornecer mais detalhes ou tentar uma busca diferente?"
    
    response = []
    for product in results:
        product_info = [
            f"Produto: {product['product_name']}",
            f"Categoria: {product['category']}",
            f"Preço: R$ {product['price']:.2f}",
            f"Descrição: {product['description']}"
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
          name="QueryProductDatabase",
          func=query_product_database,
          description=query_product_database.__doc__
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
  