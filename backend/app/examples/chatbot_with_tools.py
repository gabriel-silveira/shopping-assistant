from warnings import filterwarnings

# Supress specific warnings
filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")
filterwarnings("ignore", category=DeprecationWarning, module="langchain")

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

# Add project root to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.milvus_service import MilvusService

def query_product_database(query: str) -> str:
    """Útil para buscar informações sobre produtos disponíveis no banco de dados da loja. 
    Use esta ferramenta quando o usuário perguntar sobre produtos específicos, preços, descrições ou estoque. 
    A entrada para esta ferramenta deve ser o nome do produto ou palavras-chave relevantes para a busca."""
    
    milvus_service = MilvusService()
    results = milvus_service.search_similar_products(query)
    
    if not results:
        return "Nenhum produto encontrado."
    
    # Formata os resultados em uma string legível
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

# Configuração do modelo de linguagem
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7
)

# Configuração das ferramentas disponíveis
tools = [
    Tool(
        name="query_product_database",
        func=query_product_database,
        description=query_product_database.__doc__
    )
]

# Template do prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """Você é um assistente virtual da CSN (Companhia Siderúrgica Nacional), especializado em atender clientes e fornecer informações sobre produtos.

REGRAS IMPORTANTES:
1. Seja sempre profissional e cortês
2. Use linguagem formal, mas amigável
3. Quando não encontrar um produto, sugira refinar a busca
4. Informe que os preços podem variar e peça para entrar em contato para cotações específicas
5. Se o cliente perguntar sobre produtos, use a ferramenta query_product_database"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Criação do agente
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Histórico da conversa
chat_history = []

print("Assistente CSN iniciado. Digite 'sair' para encerrar.\n")

while True:
    # Recebe entrada do usuário
    user_input = input("Você: ")
    
    # Verifica se o usuário quer sair
    if user_input.lower() == 'sair':
        break
        
    # Processa a entrada do usuário
    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    
    # Atualiza o histórico
    chat_history.extend([
        HumanMessage(content=user_input),
        AIMessage(content=result["output"])
    ])
    
    # Mostra a resposta
    print("\nAssistente:", result["output"], "\n")
