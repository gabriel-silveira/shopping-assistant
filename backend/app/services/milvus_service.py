from typing import List, Dict, Optional
import os
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import markdown
import re
from openai import OpenAI
import numpy as np

class MilvusService:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        """Initialize connection to Milvus."""
        self.host = host
        self.port = port
        self.collection_name = "products"
        self.dim = 1536  # Dimensão do modelo text-embedding-3-small da OpenAI
        self.client = OpenAI()  # Inicializa o cliente OpenAI
        self._connect()
        self._ensure_collection()

    def _connect(self):
        """Connect to Milvus server."""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            print(f"Successfully connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise

    def _ensure_collection(self):
        """Ensure collection exists with correct schema."""
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="product_name", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="price", dtype=DataType.DOUBLE),
                FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            schema = CollectionSchema(fields=fields, description="Product catalog from markdown files")
            collection = Collection(name=self.collection_name, schema=schema)
            
            # Create index for vector field
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            print(f"Created collection {self.collection_name} with schema")
        else:
            print(f"Collection {self.collection_name} already exists")

    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding from OpenAI API.
        Uses the text-embedding-3-small model which is mais barato e rápido.
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding from OpenAI: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dim

    def _parse_markdown_file(self, file_path: str) -> Dict:
        """
        Parse markdown file to extract product information.
        Expected markdown format:
        
        # Product Name
        
        **Price**: R$ 99.99
        **Category**: Electronics
        
        ## Description
        Detailed product description here...
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Convert markdown to HTML
            html = markdown.markdown(content)
            
            # Extract product name (first h1)
            product_name = re.search(r'<h1>(.*?)</h1>', html)
            product_name = product_name.group(1) if product_name else ""
            
            # Extract price
            price = re.search(r'Price[:\s]*R\$\s*([\d.,]+)', content)
            price = float(price.group(1).replace('.', '').replace(',', '.')) if price else 0.0
            
            # Extract category
            category = re.search(r'Category[:\s]*([\w\s]+)', content)
            category = category.group(1).strip() if category else ""
            
            # Extract description (everything after ## Description)
            description = re.search(r'## Description\s+(.*?)(?=##|$)', content, re.DOTALL)
            description = description.group(1).strip() if description else ""
            
            return {
                "product_name": product_name,
                "price": price,
                "category": category,
                "description": description
            }
        except Exception as e:
            print(f"Error parsing markdown file {file_path}: {e}")
            return {}

    def import_products_from_markdown(self, markdown_dir: str):
        """
        Import products from markdown files in the specified directory.
        Each markdown file should contain information about one product.
        """
        try:
            collection = Collection(self.collection_name)
            
            product_data = []
            embeddings = []
            
            # Process each markdown file
            for filename in os.listdir(markdown_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(markdown_dir, filename)
                    product = self._parse_markdown_file(file_path)
                    
                    if product:
                        # Combine product name and description for embedding
                        text_for_embedding = f"{product['product_name']} {product['description']}"
                        
                        # Get embedding from OpenAI
                        embedding = self._get_embedding(text_for_embedding)
                        
                        product_data.append([
                            product['product_name'],
                            product['description'],
                            product['price'],
                            product['category']
                        ])
                        embeddings.append(embedding)
            
            if product_data:
                # Insert data into collection
                collection.insert([
                    product_data,  # Entity data
                    embeddings    # Vector data
                ])
                print(f"Successfully imported {len(product_data)} products")
            
            # Create index if not exists
            collection.create_index(field_name="embedding", index_params={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            })
            
            # Load collection for searching
            collection.load()
            
        except Exception as e:
            print(f"Error importing products: {e}")

    def search_similar_products(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar products in Milvus.
        
        Args:
            query_text: Text to search for (will be converted to vector using OpenAI)
            top_k: Number of similar products to return
            
        Returns:
            List of dictionaries containing product information and similarity score
        """
        try:
            # Get the collection
            collection = Collection(self.collection_name)
            collection.load()

            # Get embedding from OpenAI
            query_vector = self._get_embedding(query_text)

            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10},
            }

            # Perform the search
            results = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["product_name", "description", "price", "category"]
            )

            # Process results
            similar_products = []
            for hits in results:
                for hit in hits:
                    product = {
                        "id": hit.id,
                        "score": hit.score,
                        "product_name": hit.entity.get("product_name"),
                        "description": hit.entity.get("description"),
                        "price": hit.entity.get("price"),
                        "category": hit.entity.get("category")
                    }
                    # Only include products with similarity score above threshold
                    if hit.score >= 0.7:  # 70% similarity threshold
                        similar_products.append(product)

            return similar_products

        except Exception as e:
            print(f"Error searching for similar products: {e}")
            return []

    def close(self):
        """Close connection to Milvus."""
        try:
            connections.disconnect("default")
            print("Successfully disconnected from Milvus")
        except Exception as e:
            print(f"Error disconnecting from Milvus: {e}")
