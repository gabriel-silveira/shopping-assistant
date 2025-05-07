# import requests
from typing import List, Dict
from langchain.tools import Tool
from data.json_data.products import products


def search_products(keyword: str) -> Dict | None | str:
    """
    Busca produtos por nome ou descrição na API de catálogo da empresa.
    Retorna nome, descrição, preço e categoria dos produtos encontrados.
    """
    try:
        products_found: List[Dict] = []

        keyword = keyword.split(" ")[0].lower()

        print(f"Searching product: {keyword}\n")

        for product in products:
            if keyword in product["name"].lower() or keyword in product["description"].lower():
                products_found.append(product)

        for product_found in products_found:
            product_found["relevance"] = 0
            product_found["relevance"] += product_found["name"].lower().count(keyword)
            product_found["relevance"] += product_found["description"].lower().count(keyword)

        products_found.sort(key=lambda x: x["relevance"], reverse=True)

        if len(products_found) == 0:
            return None

        print(f"Product found: {products_found[0]}\n")

        return products_found[0]

    except Exception as e:
        return f"Erro ao buscar produto: {e}"


search_product_tool = Tool(
    name="SearchProducts",
    func=search_products,
    description=search_products.__doc__,
)
