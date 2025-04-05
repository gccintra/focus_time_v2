# Doing (MVP):

- [x] Autenticação com JWT
    - [x] Register
    - [x] Login
    - [x] FrontEnd Page Reponsiva (DOING)
    - [x] enviar para a tela de login caso o usario não esteja autenticado/token expirado (ver qual a melhor forma, redirecionar direto ou enviar um erro 401 e tratar isso em outro lugar, fora do decorador.)
    - [x] ao tentar acessar a página de login já autenticado, encaminhar para a tela principal /task
    - [x] Logout
    - https://www.youtube.com/watch?v=z92CWqvefr0&ab_channel=Spacedevs
    - https://www.youtube.com/watch?v=sHyoMWnnLGU&ab_channel=MatheusBattisti-HoradeCodar
    - [x] Salvar token em cookies
    - [x] Cryptografar senha para salvar no banco
- [x] WebSocket -> Apresentar todos os usuarios online, e se estão em foco em alguma tarefa, apresentar o tempo que estao em foco tambem.
- [x] WebSocket -> Alterar o ícone, deixar maior.

- [x] Unicidade de e-mail e username.
- [x] Requisitos Minimos Senha

- [x] Validações de campo
    - [x] Front-end
        - [x] Incluir tamanho maximo de caracteres
        - [x] Campo Vazio
    - [x] Back-end
        - [x] Incluir tamanho maximo de caracteres
        - [x] Campo Vazio

- [x] Getters e Setters, + Segurança
    - [x] Validações ao tentar criar uma task com id igual (hard coded)

- [x] Padrão de dados retornados para o front-end (TASKS)
- [x] Tratamento de Erros e Apresentação de Mensagens (Front-End)
    - [x] To Do
    - [x] Tasks
- [x] Ordenação das tasks por maior porcentagem. (ta com bug)

- [x] Encapsulamento e validações de models.

- [ ] Testes  
    - [x] Models
    - [ ] Testes de Integração
    - [ ] Controllers
    - [ ] Services
    - [ ] Repositories


- [ ] Adicionar cache em memória usando bibliotecas como functools.lru_cache.

- [ ] verificações de metodos na requisição do backend (post, get etc)


- [ ] Dockerizar
- [ ] mudar a nomeclatura do 'start_task'
- [ ] Bug nos dias (365)
    - [ ] Domingo (Não cria uma nova week)
    - [x] Segunda e Terça (o layout quebra, não elimina a primeira semana na esquerda)




# To do:

- [ ] Docker + Banco de Dados


- [ ] Delete e Edit Task
- [ ] Edit To Do
- [ ] Edit, Delete User

- [ ] Travar multiplas requisições ao pressionar o botão diversas vezes
- [ ] Layout de Today e Week na página principal

- [ ] Websocket -> Confirmar Presença (enviar notificação) de 60 em 60 minutos, caso a presença não seja confirmada o tempo de foco é pausado
- [x] Deixar o toast mais bonito
- [x] last 365 days
- [ ] ToDo para cada task
    - [x] BackEnd: Create
    - [x] Validação do nome do status
    - [x] FrontEnd: Apresentação das tasks
    - [x] Delete
    - [x] Info: Created Time and Completed Time
    - [ ] To Do List Filtros (por data de criação/finalização)
    - [ ] Prioridade
- [x] BUG: Ao criar nova task, tem que criar o gráfico tambem. (Atualizar no arquivo js)
- [x] Abstrair mais o codigo (templates, js, partials, mais classes, rotas)
- [x] Refatorar pesado aqui (+segurança, melhorar a manipulação dos dados (dicionário x instâncias), melhorar os models.)
- [x] Melhorar DB Tabelas (Task, ToDo)
- [x] ToDo Blueprint
- [x] Classe exeption
- [x] logging
- [x] Tratamento de Erros (Back-End)
- [ ] configurar logging do flask: https://flask.palletsprojects.com/en/stable/logging/
- [x] Estudar e Melhorar os blueprints
- [x] REFATORAR TUDO, TENDO EM VISTA A REFATORACAO DE DATA_RECORD 
- [x] SEPARAR CONTROLLER E ROUTES (ta tudo junto hoje em dia)
- [x] Salvar o seconds_in_focus_per_day a todo segundo, e não somente quando o usuário clicar em stop. (para salvar o tempo msm se o usuário sair dar tela, fechar a tela, perder conexão com internet.)
- [x] Gráfico do git hub
- [x] Separar melhor as pastas dos arquivos 
- [ ] Factory + Injeção de Dependências

Pensar no cenário onde o timer foi iniciado antes da 00:00 e continuou até após 00:00

- [x] Salvar o tempo em segundos no banco...
- [ ] salvar em banco de dados inves de arquivo
- [ ] my perfomance
- [ ] edit e delete


