from typing import List, Dict, Union
import os
import re
import unicodedata
import markdown

class MarkdownSearchService:
    def __init__(self, products_dir: str = "/home/gabriel-silveira/Projects/shopping-assistant/backend/data/products"):
        self.products_dir = products_dir

    def _normalize_text(self, text: str) -> str:
        """Remove acentos e converte para minúsculas"""
        return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')

    def _parse_markdown_file(self, file_path: str) -> Dict:
        """Parse um arquivo markdown de produto e retorna suas informações"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Converte markdown para HTML
            html = markdown.markdown(content)
            
            # Extrai nome do produto (primeiro h1)
            product_name = re.search(r'<h1>(.*?)</h1>', html)
            product_name = product_name.group(1) if product_name else ""
            
            # Extrai preço
            price = re.search(r'Price[:\s]*R\$\s*([\d.,]+)', content)
            price = float(price.group(1).replace('.', '').replace(',', '.')) if price else 0.0
            
            # Extrai categoria
            category = re.search(r'\*\*Category\*\*:\s*([\w\s\/]+)', content)
            category = category.group(1).strip() if category else ""
            
            # Extrai descrição (tudo após ## Description até o fim do arquivo)
            description = re.search(r'## Description\s*\n([\s\S]*?)$', content)
            description = description.group(1).strip() if description else ""
            
            return {
                "product_name": product_name,
                "price": price,
                "category": category,
                "description": description,
                "file_path": file_path  # Útil para debug
            }
        except Exception as e:
            print(f"Error parsing markdown file {file_path}: {e}")
            return {}

    def search_products(self, query: str) -> List[Dict]:
        """
        Busca produtos nos arquivos markdown baseado em palavras-chave.
        Retorna uma lista de produtos que correspondem à busca.
        """
        # Normaliza a query
        query_normalized = self._normalize_text(query)
        query_terms = query_normalized.split()
        
        results = []
        
        # Lista todos os arquivos .md no diretório de produtos
        for filename in os.listdir(self.products_dir):
            if filename.endswith('.md') and not filename.startswith('template'):
                file_path = os.path.join(self.products_dir, filename)
                product_info = self._parse_markdown_file(file_path)
                
                if not product_info:
                    continue
                
                # Normaliza os campos do produto para busca
                searchable_text = self._normalize_text(
                    f"{product_info['product_name']} {product_info['category']} {product_info['description']}"
                )
                
                # Calcula relevância baseada em quantos termos da busca aparecem no texto
                matches = sum(1 for term in query_terms if term in searchable_text)
                if matches > 0:
                    product_info['relevance'] = matches
                    results.append(product_info)
        
        # Ordena por relevância
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        if not results:
            return []
            
        return results

    def get_all_products(self) -> List[Dict]:
        """Retorna todos os produtos disponíveis"""
        results = []
        
        for filename in os.listdir(self.products_dir):
            if filename.endswith('.md') and not filename.startswith('template'):
                file_path = os.path.join(self.products_dir, filename)
                product_info = self._parse_markdown_file(file_path)
                if product_info:
                    results.append(product_info)
        
        return results
