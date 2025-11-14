# MeuScrum

Sistema de gerenciamento de projetos Scrum desenvolvido em Flask.

## Requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. **Clone o repositório ou navegue até a pasta do projeto:**
   ```bash
   cd MeuScrum
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o banco de dados PostgreSQL:**
   - Crie um banco de dados chamado `BDMeuScrum`
   - Execute o script SQL `BDMeuScrum - SQL.sql` para criar as tabelas
   - Ajuste as credenciais em `database.py` se necessário:
     - hostname: 'localhost'
     - database: 'BDMeuScrum'
     - username: 'postgres'
     - password: 'admin' (altere conforme necessário)
     - port: 5432

4. **Execute o servidor:**
   ```bash
   python app.py
   ```

5. **Acesse o sistema:**
   - Abra seu navegador e acesse: `http://localhost:5000`

## Estrutura do Projeto

```
MeuScrum/
├── app.py                 # Aplicação Flask principal
├── database.py            # Funções de acesso ao banco de dados
├── requirements.txt       # Dependências Python
├── BDMeuScrum - SQL.sql  # Script de criação do banco de dados
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── home.html
│   ├── projeto.html
│   ├── backlog.html
│   ├── sprint.html
│   ├── plano-sprint.html
│   └── configuracoes.html
├── static/
│   ├── css/
│   │   └── style.css      # Estilos CSS
│   └── js/
│       └── main.js        # JavaScript global
└── Imagens/
    └── logo.png           # Logo do sistema
```

## Funcionalidades

### Autenticação
- Login de usuários
- Registro de novos usuários
- Logout

### Gerenciamento de Projetos
- Criar projetos
- Visualizar projetos do usuário
- Gerenciar status de projetos
- Adicionar usuários aos projetos

### Backlog de Produto
- Criar e gerenciar User Stories
- Definir prioridades
- Atualizar status
- Associar responsáveis

### Sprints
- Criar sprints
- Gerenciar backlog da sprint
- Visualizar user stories da sprint
- Atualizar status da sprint

### Plano de Sprint
- Definir objetivo da sprint
- Planejar trabalho
- Definir equipe
- Especificar saída esperada
- Gerenciar tarefas

### Tarefas
- Criar tarefas
- Atualizar status
- Associar responsáveis
- Marcar como concluída

### Configurações
- Atualizar dados do usuário
- Alterar senha

## Uso

1. **Primeiro acesso:**
   - Acesse a tela de login
   - Clique em "Cadastre-se" para criar uma conta
   - Preencha CPF, Nome, Email e Senha
   - Faça login com suas credenciais

2. **Criar um projeto:**
   - Na tela inicial (Home), clique em "+ Novo Projeto"
   - Preencha o nome, data de término (opcional) e status
   - O backlog de produto será criado automaticamente

3. **Gerenciar Backlog:**
   - Acesse o projeto
   - Clique em "Backlog de Produto"
   - Crie User Stories com título, descrição, prioridade e status

4. **Criar Sprint:**
   - Na página do projeto, clique em "+ Nova Sprint"
   - Defina título, datas e status
   - O backlog da sprint e o plano serão criados automaticamente

5. **Planejar Sprint:**
   - Acesse a sprint
   - Clique em "Plano de Sprint"
   - Preencha objetivo, trabalho, equipe e saída esperada
   - Adicione tarefas conforme necessário

