# FocusTime

## 📌 Sobre a Aplicação

O FocusTime é um sistema de gerenciamento de tempo que permite aos usuários se concentrarem em suas tarefas enquanto monitoram e interagem com outros usuários em sessões de foco. O sistema utiliza Flask como backend e WebSockets para comunicação em tempo real.

## 🚀 Tecnologias Utilizadas

Backend: Python, Flask, Flask-SocketIO, Flask-JWT-Extended

Frontend: HTML, CSS (Bootstrap), JavaScript

Autenticação: JWT (JSON Web Token) com armazenamento em cookies

## ⚙️ Funcionalidades

### Autenticação de Usuários

- Registro e login de usuários
- Autenticação via JWT armazenado em cookies
- Logout seguro com revogação de tokens

### Gerenciamento de Sessões de Foco

- Usuários podem ingressar em "salas" de foco distintas
- Lista de usuários ativos em cada sessão é atualizada em tempo real

### Gerenciamento de Tarefas

- Criar, listar e gerenciar tarefas
- Registro de tempo gasto em cada tarefa
- Análises de produtividade com gráficos

## 🔌 Configuração e Execução

### 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/gccintra/focus_time
```

Crie um ambiente virtual e ative-o:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure a variável de ambiente do Flask:

```bash
export FLASK_APP=app
export FLASK_ENV=development
```

### ▶️ Executando a Aplicação

Para iniciar o servidor Flask com WebSockets ativados:

```bash
flask run
```
                        
A aplicação estará disponível em: http://127.0.0.1:5000/
