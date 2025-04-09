# Histórico de Desenvolvimento do Chatbot da Câmara Espanhola

Este documento apresenta o histórico completo do desenvolvimento do chatbot para a Câmara Oficial Espanhola de Comércio no Brasil, detalhando cada etapa, abordagem, arquivos gerados e resultados obtidos.

## Visão Geral do Projeto

O projeto consistiu no desenvolvimento de um chatbot inteligente para a Câmara Espanhola que recupera informações de documentos PDF indexados usando Pinecone e gera respostas usando OpenAI. O chatbot foi projetado para ser integrado em uma interface web amigável e visualmente atraente.

## Etapas de Desenvolvimento

### 1. Indexação de Documentos

**Abordagem:** Criamos um script para extrair texto de documentos PDF e indexá-los no Pinecone.

**Arquivos Gerados:**
- `index_pdfs.py`: Script para extrair texto de PDFs e indexá-los no Pinecone usando o modelo `text-embedding-3-large` da OpenAI.

**Resultados:** Os documentos foram indexados com sucesso no Pinecone, permitindo buscas semânticas eficientes.

### 2. Desenvolvimento do Servidor do Chatbot

**Abordagem:** Implementamos várias versões do servidor do chatbot para testar diferentes abordagens e funcionalidades.

**Arquivos Gerados:**
- `original_chatbot_server.py`: Versão estável inicial do servidor Flask.
- `formatted_chatbot_server.py`: Versão com formatação aprimorada para listas numeradas e markdown.
- `smart_chatbot_server.py`: Versão experimental com formatação (potencialmente instável).
- `direct_chatbot.py`: Implementação direta usando Flask.
- `chatbot_embed.py` e `chatbot_embed_fixed.py`: Versões para uso com Streamlit.

**Resultados:** Conseguimos uma versão funcional do chatbot que recupera informações precisas dos documentos indexados e apresenta respostas bem formatadas.

### 3. Desenvolvimento da Interface Web

**Abordagem:** Criamos uma interface web responsiva e amigável para o chatbot.

**Arquivos Gerados:**
- `static/index.html`: Página principal do site com o chatbot integrado.
- `static/css/styles.css`: Estilos CSS para o site e chatbot.
- `static/js/chatbot.js`: JavaScript para a funcionalidade do chatbot.
- Outras variações como `index_direct.html`, `index_new.html`, `complete_solution.html` e `chatbot.html`.

**Resultados:** Conseguimos uma interface flutuante que pode ser minimizada/maximizada e se integra bem ao site da Câmara Espanhola.

### 4. Preparação para Deploy

**Abordagem:** Preparamos o projeto para deploy no Netlify (frontend) e Render (backend).

**Arquivos Gerados:**
- `backend_api/api_server.py`: Servidor Flask para a API do chatbot.
- `backend_api/requirements.txt`: Dependências do backend.
- `netlify.toml`: Configuração para deploy no Netlify.

**Resultados:** O projeto foi estruturado para facilitar o deploy em plataformas de hospedagem modernas.

### 5. Deploy no Netlify e Render

**Abordagem:** Tentamos fazer o deploy do frontend no Netlify e do backend no Render.

**Arquivos Modificados:**
- `netlify.toml`: Atualizado para apontar para o backend no Render.
- `backend_api/api_server.py`: Corrigido para compatibilidade com o Render.
- `backend_api/requirements.txt`: Atualizado com as versões corretas das dependências.

**Resultados:** Enfrentamos alguns problemas com a inicialização do Pinecone no Render devido a incompatibilidades de versão.

### 6. Correções de Compatibilidade com o Pinecone

**Abordagem:** Identificamos que estávamos usando uma sintaxe incompatível com a versão do Pinecone especificada no `requirements.txt`.

**Arquivos Modificados:**
- `backend_api/api_server.py`: Corrigida a inicialização do Pinecone para usar a sintaxe correta.
- `backend_api/requirements.txt`: Atualizada a versão do Pinecone para 2.0.0.
- `backend_api/.env.example`: Atualizado para incluir a variável `ENVIRONMENT`.

**Commit:** "Fix Pinecone initialization for compatibility with version 2.0.0"
**Detalhes:** Este commit corrigiu a inicialização do cliente Pinecone para usar a sintaxe correta da versão 2.0.0, que usa `pinecone.init()` em vez de `pinecone.Pinecone()`.

### 7. Atualização da Versão do Pinecone

**Abordagem:** Identificamos que a versão 2.0.0 do Pinecone tinha problemas de compatibilidade com Python 3.11 no Render.

**Arquivos Modificados:**
- `backend_api/api_server.py`: Atualizada a inicialização do Pinecone para a versão 2.2.1.
- `backend_api/requirements.txt`: Atualizada a versão do Pinecone para 2.2.1.

**Commit:** "Update Pinecone to version 2.2.1 for Python 3.11 compatibility"
**Detalhes:** Este commit atualizou a versão do Pinecone para 2.2.1, que é compatível com Python 3.11, e ajustou a inicialização do cliente para usar a sintaxe correta.

### 8. Atualização do URL do Backend no Netlify

**Abordagem:** Atualizamos o arquivo `netlify.toml` para apontar para o URL correto do backend no Render.

**Arquivos Modificados:**
- `netlify.toml`: Atualizado o URL do backend para `https://camara-vcy4.onrender.com`.

**Commit:** "Update netlify.toml to point to the correct Render backend URL"
**Detalhes:** Este commit atualizou o redirecionamento no arquivo `netlify.toml` para apontar para o URL correto do backend no Render.

### 9. Exploração de Alternativas de Deploy

**Abordagem:** Devido a dificuldades com o Render, exploramos alternativas de deploy, incluindo PythonAnywhere.

**Arquivos Gerados:**
- `pythonanywhere_deploy/flask_app.py`: Versão simplificada do chatbot para deploy no PythonAnywhere.
- `pythonanywhere_deploy/requirements.txt`: Dependências simplificadas.
- `pythonanywhere_deploy/.env.example`: Exemplo de variáveis de ambiente.
- `pythonanywhere_deploy/README.md`: Instruções detalhadas para deploy.

**Commit:** "Adicionar opção de deploy no PythonAnywhere como alternativa ao Netlify/Render"
**Detalhes:** Este commit adicionou uma opção alternativa de deploy usando o PythonAnywhere, que é mais simples e tem um plano gratuito adequado para testes.

### 10. Versão Simplificada para PythonAnywhere

**Abordagem:** Criamos uma versão simplificada do chatbot que não depende do Pinecone ou OpenAI para facilitar o deploy no PythonAnywhere.

**Arquivos Gerados:**
- `pythonanywhere_deploy/flask_app.py`: Versão simplificada com respostas pré-definidas.
- `pythonanywhere_deploy/requirements.txt`: Dependências mínimas.
- `pythonanywhere_deploy/.env.example`: Exemplo simplificado.
- `pythonanywhere_deploy/wsgi_config.py`: Configuração WSGI para PythonAnywhere.

**Resultados:** A versão simplificada foi implantada com sucesso no PythonAnywhere, mas não atendia ao requisito de usar busca semântica com Pinecone.

### 11. Correção para Compatibilidade do OpenAI no PythonAnywhere

**Abordagem:** Identificamos que o PythonAnywhere estava tentando adicionar um argumento `proxies` ao cliente OpenAI, causando erros.

**Arquivos Modificados:**
- `backend_api/api_server.py`: Modificada a inicialização do cliente OpenAI para lidar com o problema de proxies.
- `backend_api/requirements.txt`: Adicionada a dependência `httpx` para lidar com o cliente HTTP personalizado.

**Commit:** "Fix OpenAI client initialization for PythonAnywhere compatibility"
**Detalhes:** Este commit adicionou uma solução para o problema de compatibilidade do OpenAI no PythonAnywhere, usando um cliente HTTP personalizado que ignora proxies.

## Desafios Superados

1. **Compatibilidade com Pinecone**: Ajustamos a dimensão e o modelo de embedding para compatibilidade com o índice existente e resolvemos problemas de versão.

2. **Formatação de Respostas**: Implementamos formatação especial para listas numeradas, subitens com bullets e markdown (negrito/itálico).

3. **Interface Responsiva**: Criamos uma interface flutuante que pode ser minimizada/maximizada e se integra bem ao site.

4. **Deploy**: Enfrentamos e resolvemos vários desafios de deploy, incluindo incompatibilidades de versão e problemas de configuração.

## Estado Atual

O projeto está em fase de deploy, com as seguintes opções disponíveis:

1. **Netlify + Render**: Frontend no Netlify e backend no Render, usando a versão completa com Pinecone e OpenAI.

2. **PythonAnywhere**: Versão simplificada com respostas pré-definidas, sem dependência de Pinecone ou OpenAI.

3. **PythonAnywhere (Versão Completa)**: Em desenvolvimento, uma versão que usa Pinecone e OpenAI no PythonAnywhere, com correções para compatibilidade.

## Próximos Passos

1. Finalizar o deploy da versão completa no PythonAnywhere ou Render.
2. Testar exaustivamente a integração entre frontend e backend.
3. Refinar as respostas do chatbot com base no feedback dos usuários.
4. Documentar o processo de manutenção e atualização do chatbot.

## Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Processamento de Documentos**: PyPDF2, OpenAI Embeddings
- **Armazenamento de Vetores**: Pinecone
- **Geração de Respostas**: OpenAI GPT-4o
- **Frontend**: HTML, CSS, JavaScript
- **Controle de Versão**: Git/GitHub
- **Plataformas de Deploy**: Netlify, Render, PythonAnywhere
