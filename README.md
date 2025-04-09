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

Existem várias maneiras de executar o chatbot, dependendo das suas necessidades:

#### Versão recomendada (testada e funcional)

Esta é a versão mais estável e testada:

```
python original_chatbot_server.py
```

O servidor estará disponível em `http://localhost:8080`. Esta versão integra o site da Câmara Espanhola com o chatbot em uma única página, utilizando Pinecone para busca de documentos e OpenAI para geração de respostas.

#### Outras versões disponíveis

1. **Versão com Streamlit:**
```
python serve.py
```
Esta versão usa o Streamlit para criar a interface do chatbot, mas pode ter problemas de carregamento em alguns casos.

2. **Versão direta com Flask:**
```
python direct_chatbot.py
```
Uma versão simplificada que usa Flask diretamente para servir o chatbot.

3. **Versão com servidor HTTP simples:**
```
python serve_complete.py
```
Uma versão que usa um servidor HTTP simples para servir uma página estática com o chatbot integrado.

## Estrutura do Projeto

### Arquivos principais

- `index_pdfs.py`: Script para extrair texto de PDFs e indexá-los no Pinecone
- `original_chatbot_server.py`: **[RECOMENDADO]** Servidor Flask que integra o site e o chatbot com Pinecone
- `formatted_chatbot_server.py`: **[NOVA VERSÃO]** Versão com formatação aprimorada para listas numeradas e markdown
- `smart_chatbot_server.py`: Versão alternativa com formatação (pode ser instável)
- `direct_chatbot.py`: Implementação direta do chatbot usando Flask
- `chatbot_embed.py` e `chatbot_embed_fixed.py`: Versões do chatbot para uso com Streamlit

### Servidores e integrações

- `serve.py`: Inicia um servidor HTTP simples e um servidor Streamlit para o chatbot
- `serve_fixed.py` e `serve_new.py`: Variações do servidor com diferentes configurações de porta
- `serve_direct.py`: Servidor para a versão direta do chatbot
- `serve_complete.py`: Servidor para a versão completa integrada em HTML

### Arquivos estáticos e templates

- `static/`: Pasta contendo arquivos estáticos para o site
  - `index.html`: Página principal do site com o chatbot integrado
  - `index_direct.html`: Versão alternativa da página principal
  - `index_new.html`: Outra variação da página principal
  - `complete_solution.html`: Solução completa em um único arquivo HTML
  - `chatbot.html`: Interface isolada do chatbot
- `templates/`: Pasta para templates do Flask
  - `index.html`: Template básico para o site

### Outras implementações

- `app.py`: Implementação original do chatbot usando Streamlit
- `app_direct.py`: Versão direta do app Streamlit
- `popup_chatbot.py` e `popup_chatbot_simple.py`: Versões iniciais do chatbot pop-up

## Como funciona

1. **Indexação de documentos:**
   - O script `index_pdfs.py` extrai texto de documentos PDF
   - Divide o texto em chunks menores
   - Gera embeddings usando a API da OpenAI
   - Armazena os embeddings no Pinecone para busca rápida

2. **Fluxo do chatbot:**
   - O usuário faz uma pergunta
   - O sistema gera um embedding para a pergunta
   - Busca no Pinecone os documentos mais relevantes
   - Envia os documentos relevantes e a pergunta para a API da OpenAI
   - Recebe e exibe a resposta gerada

## Solução de problemas

- Se o chatbot não aparecer, verifique se os servidores estão rodando nas portas corretas
- Se as respostas não forem relevantes, verifique se os documentos foram indexados corretamente
- Se o chatbot travar, tente usar a versão `original_chatbot_server.py` que é mais estável

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
