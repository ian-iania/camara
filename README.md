# Chatbot da Câmara Espanhola

Um chatbot inteligente para a Câmara Oficial Espanhola de Comércio no Brasil, que responde a perguntas com base em documentos indexados.

## Funcionalidades

- Interface de chat pop-up que aparece no canto inferior direito da página
- Recuperação de informações de documentos PDF indexados
- Integração com Pinecone para armazenamento e busca de vetores
- Integração com OpenAI para geração de respostas relevantes
- Manutenção de histórico de conversas para contexto

## Requisitos

- Python 3.8+
- Pinecone API Key
- OpenAI API Key

## Instalação

1. Clone o repositório:
```
git clone https://github.com/ian-iania/camara.git
cd camara
```

2. Crie um ambiente virtual e instale as dependências:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com suas chaves de API:
```
PINECONE_API_KEY=sua_chave_pinecone
OPENAI_API_KEY=sua_chave_openai
```

## Uso

### Indexação de documentos

Para indexar novos documentos PDF:

```
python index_pdfs.py
```

Os PDFs devem estar na pasta `PDFs/`.

### Executando o chatbot

Para iniciar o servidor com o chatbot:

```
python original_chatbot_server.py
```

O servidor estará disponível em `http://localhost:8080`.

## Estrutura do Projeto

- `index_pdfs.py`: Script para extrair texto de PDFs e indexá-los no Pinecone
- `original_chatbot_server.py`: Servidor Flask que integra o site e o chatbot
- `static/`: Pasta contendo arquivos estáticos para o site
- `PDFs/`: Pasta para armazenar os documentos PDF a serem indexados

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
