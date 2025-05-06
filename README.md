# Shopping Assistant Chatbot

Um assistente de chat inteligente para coletar informações de orçamentos de clientes.

## Tecnologias Utilizadas

- Backend:
  - FastAPI
  - LangChain
  - LangGraph
  - Pydantic
  - Milvus
  - OpenAI

- Frontend:
  - Next.js
  - TailwindCSS
  - TypeScript

## Estrutura do Projeto

```
shopping-assistant/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── models/   # Modelos Pydantic
│   │   ├── graph/    # Fluxo de conversa LangGraph
│   │   ├── prompts/  # Prompts
│   │   ├── services/ # Serviços de banco de dados e outros
│   │   ├── tools/    # Ferramentas utilizadas no fluxo de conversa
│   │   └── core/     # Lógica principal
│   └── requirements.txt
└── frontend/         # Interface Next.js
    ├── components/   # Componentes React
    ├── pages/       # Páginas da aplicação
    └── styles/      # Estilos CSS
```

## Como Executar

### 1. Criar o banco de dados Milvus (Docker):
```bash
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

bash standalone_embed.sh start
```

### 2. Importar produtos:
```bash
cd backend
python -m venv venv
source venv/bin/activate
python import_products.py
```

### 3. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --log-level debug

# Alternativa: ativa o ambiente virtual, instala dependências e inicia a aplicação
source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --log-level debug
```

### 4. Frontend:
```bash
cd frontend
npm install
npm run dev
```
