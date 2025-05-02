from app.services.milvus_service import MilvusService

# Inicializar o serviço
milvus = MilvusService()

# Buscar produtos similares
product_query = "quente"
print(f"\nBuscando por: {product_query}")
print("-" * 50)

results = milvus.search_similar_products(product_query)

# Processar resultados
if results:
    for product in results:
        print(f"Produto: {product['product_name']}")
        print(f"Preço: R$ {product['price']:.2f}")
        print(f"Categoria: {product['category']}")
        print(f"Similaridade: {product['score']:.2%}")
        if product['description']:
            print(f"Descrição: {product['description'][:200]}...")
        print("-" * 50)

    print(f"\nTotal encontrados: {len(results)}")
else:
    print("Nenhum produto encontrado")