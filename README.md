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
│   │   └── core/     # Lógica principal
│   └── requirements.txt
└── frontend/         # Interface Next.js
    ├── components/   # Componentes React
    ├── pages/       # Páginas da aplicação
    └── styles/      # Estilos CSS
```

## Como Executar

1. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm run dev
```
