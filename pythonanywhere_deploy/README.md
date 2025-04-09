# Deploy do Chatbot da Câmara Espanhola no PythonAnywhere

Este diretório contém os arquivos necessários para fazer o deploy do Chatbot da Câmara Espanhola no PythonAnywhere, uma plataforma de hospedagem especializada em Python que oferece um plano gratuito adequado para testes.

## Arquivos Incluídos

- `flask_app.py` - Aplicação Flask completa com frontend e backend integrados
- `requirements.txt` - Dependências necessárias para o projeto
- `.env.example` - Exemplo de arquivo de variáveis de ambiente (você precisará criar um arquivo `.env` real)

## Instruções de Deploy

### 1. Criar uma Conta no PythonAnywhere

1. Acesse [PythonAnywhere](https://www.pythonanywhere.com/) e crie uma conta gratuita
2. Após o login, vá para o Dashboard

### 2. Configurar um Web App

1. No Dashboard, clique em "Web" na barra de navegação superior
2. Clique em "Add a new web app"
3. Escolha "Manual configuration"
4. Selecione a versão mais recente do Python (3.9 ou superior)
5. Clique em "Next" e o app será criado

### 3. Fazer Upload dos Arquivos

1. No Dashboard, clique em "Files" na barra de navegação superior
2. Navegue até o diretório do seu web app (geralmente `/home/seuusername/mysite/`)
3. Faça upload dos arquivos deste diretório (`flask_app.py`, `requirements.txt`)
4. Crie um arquivo `.env` baseado no `.env.example` e adicione suas chaves de API

### 4. Configurar o Ambiente Virtual

1. No Dashboard, clique em "Consoles" na barra de navegação superior
2. Inicie um novo console Bash
3. Execute os seguintes comandos:

```bash
cd ~/mysite
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurar o WSGI File

1. No Dashboard, clique em "Web" na barra de navegação superior
2. Clique em "WSGI configuration file" na seção "Code"
3. Edite o arquivo para apontar para sua aplicação Flask:

```python
import sys
import os
from dotenv import load_dotenv

# Adicione o diretório do seu projeto ao path
path = '/home/seuusername/mysite'
if path not in sys.path:
    sys.path.append(path)

# Carregue as variáveis de ambiente
load_dotenv(os.path.join(path, '.env'))

# Importe sua aplicação Flask
from flask_app import app as application
```

4. Salve o arquivo

### 6. Reiniciar o Web App

1. No Dashboard, clique em "Web" na barra de navegação superior
2. Clique no botão "Reload" para o seu web app

### 7. Acessar o Chatbot

Seu chatbot agora estará disponível em:
`https://seuusername.pythonanywhere.com`

## Solução de Problemas

- **Erro de Importação**: Verifique se todas as dependências foram instaladas corretamente
- **Erro de API Key**: Verifique se o arquivo `.env` foi criado corretamente com suas chaves de API
- **Erro 500**: Verifique os logs de erro na seção "Web" > "Logs"

## Limitações do Plano Gratuito

- CPU e RAM limitados
- Tráfego limitado
- O site fica inativo após 3 meses sem atualizações
- Domínio limitado a `seuusername.pythonanywhere.com`

Para uso em produção, considere fazer upgrade para um plano pago.
