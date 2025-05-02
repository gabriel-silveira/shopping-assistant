from langchain_core.tools import tool
from app.services.milvus_service import MilvusService

@tool
def query_product_database(query: str):
    """Útil para buscar informações sobre produtos disponíveis no banco de dados da loja. 
    Use esta ferramenta quando o usuário perguntar sobre produtos específicos, preços, descrições ou estoque. 
    A entrada para esta ferramenta deve ser o nome do produto ou palavras-chave relevantes para a busca (ex: 'cimento', 'embalagem', 'ferro do granulado', 'latas de aço')."""

    milvus_service = MilvusService()
    results = milvus_service.search_similar_products(query)
    return results

# Let's inspect some of the attributes associated with the tool.
#print(query_product_database.name)
#print(query_product_database.description)
#print(query_product_database.args)