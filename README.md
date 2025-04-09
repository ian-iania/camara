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
- `serve_complete.py`: Versão que usa um servidor HTTP simples para servir uma página estática com o chatbot integrado

### Arquivos para deploy

- `static/`: Diretório com arquivos estáticos para deploy no Netlify
  - `index.html`: Página principal do site
  - `css/styles.css`: Estilos CSS para o site e chatbot
  - `js/chatbot.js`: JavaScript para a funcionalidade do chatbot
- `backend_api/`: Diretório com o backend para deploy no Render
  - `api_server.py`: Servidor Flask para a API do chatbot
  - `requirements.txt`: Dependências do backend
  - `Procfile`: Configuração para deploy no Render
- `netlify.toml`: Configuração para deploy no Netlify

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

Se você encontrar algum problema ao executar o chatbot, verifique:

1. Se as chaves de API do Pinecone e OpenAI estão configuradas corretamente no arquivo `.env`
2. Se o índice do Pinecone existe e está configurado corretamente
3. Se todas as dependências estão instaladas
4. Se o servidor está rodando na porta correta (8080 por padrão)
5. Se o chatbot não aparecer, verifique se os servidores estão rodando nas portas corretas
6. Se as respostas não forem relevantes, verifique se os documentos foram indexados corretamente
7. Se o chatbot travar, tente usar a versão `original_chatbot_server.py` que é mais estável

## Deploy

### Deploy no Netlify (Frontend)

Para fazer o deploy do frontend no Netlify:

1. Crie uma conta no [Netlify](https://www.netlify.com/)
2. Instale a CLI do Netlify:
   ```
   npm install -g netlify-cli
   ```
3. Faça login na sua conta:
   ```
   netlify login
   ```
4. Inicie o deploy:
   ```
   netlify deploy --prod
   ```
5. Quando solicitado, especifique o diretório `static` como o diretório de publicação

Alternativamente, você pode fazer o deploy diretamente pelo site do Netlify, arrastando e soltando a pasta `static` na interface de upload.

### Deploy no Render (Backend)

Para fazer o deploy do backend no Render:

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service
3. Conecte seu repositório GitHub ou faça upload do código
4. Configure as seguintes opções:
   - **Nome**: camara-chatbot-api
   - **Ambiente**: Python
   - **Diretório de Construção**: backend_api
   - **Comando de Inicialização**: gunicorn api_server:app
5. Adicione as variáveis de ambiente:
   - `PINECONE_API_KEY`: Sua chave de API do Pinecone
   - `OPENAI_API_KEY`: Sua chave de API do OpenAI
   - `ENVIRONMENT`: Seu ambiente do Pinecone (geralmente "gcp-starter")
6. Clique em "Create Web Service"

Após o deploy, atualize o arquivo `netlify.toml` com o URL do seu serviço no Render.

### Deploy no PythonAnywhere (Solução Alternativa)

Se você estiver enfrentando problemas com o Netlify e o Render, o PythonAnywhere é uma excelente alternativa para deploy, especialmente para testes:

1. **Preparação**:
   - Use os arquivos na pasta `pythonanywhere_deploy/`
   - Esta versão combina frontend e backend em uma única aplicação Flask

2. **Passos para Deploy**:
   - Crie uma conta gratuita no [PythonAnywhere](https://www.pythonanywhere.com/)
   - No Dashboard, clique em "Web" e depois "Add a new web app"
   - Escolha "Manual configuration" e selecione Python 3.9+
   - Faça upload dos arquivos da pasta `pythonanywhere_deploy/` para sua conta
   - Crie um ambiente virtual e instale as dependências:
     ```
     cd ~/mysite
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```
   - Configure o arquivo WSGI para apontar para sua aplicação
   - Adicione suas variáveis de ambiente (PINECONE_API_KEY, OPENAI_API_KEY, ENVIRONMENT)
   - Reinicie o web app

3. **Vantagens**:
   - Plano gratuito adequado para testes
   - Solução tudo-em-um (frontend + backend)
   - Especializado em hospedagem Python
   - Interface simples de usar

Para instruções detalhadas, consulte o README na pasta `pythonanywhere_deploy/`.

Depois de fazer o deploy do frontend e do backend, você precisa:

1. Atualizar o redirecionamento no arquivo `netlify.toml` para apontar para o URL do seu backend
2. Fazer o redeploy do frontend para aplicar as alterações

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
