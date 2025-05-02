from app.services.milvus_service import MilvusService

# Inicializar o serviço
milvus = MilvusService()

# Recriar a collection (isso vai apagar todos os dados existentes)
milvus.recreate_collection()

# Importar produtos dos arquivos markdown
milvus.import_products_from_markdown("data/products/acos_planos/laminados_a_quente")