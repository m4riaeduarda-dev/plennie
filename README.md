# Plennie 💰

**Plennie — Aplicativo de organização financeira pessoal**

## 1. Sobre o projeto

O Plennie é um projeto acadêmico em desenvolvimento que tem como objetivo auxiliar os usuários na organização de suas finanças pessoais. A proposta é oferecer uma interface simples e intuitiva para acompanhar despesas, dívidas e outras informações financeiras, facilitando o controle do orçamento.

O projeto está sendo desenvolvido com foco em sua utilização em dispositivos Android.

## 2. Objetivos

- Facilitar o controle das finanças pessoais.
- Permitir o registro e a consulta de despesas.
- Organizar informações financeiras em uma interface intuitiva.
- Implementar um backend para processar e armazenar os dados.
- Utilizar um banco de dados para persistir as informações.
- Preparar a aplicação para utilização em dispositivos Android.

## 3. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| HTML5 | Estrutura da interface |
| CSS3 | Estilização e layout |
| JavaScript | Interatividade e comunicação com o backend |
| Python | Linguagem utilizada no backend |
| Flask | Desenvolvimento da API |
| SQLite | Armazenamento de dados |
| Git e GitHub | Controle de versão e colaboração |

## 4. Estrutura do projeto

```text
plennie/
├── app.py
├── database.py
├── plennie.db
├── index.html
├── index-backup.html
├── teste_api.py
├── README.md
└── .venv/
```

**Descrição dos principais arquivos:**

- `app.py`: inicialização do servidor Flask e implementação dos endpoints da API.
- `database.py`: configuração da conexão com o banco de dados e criação das tabelas.
- `plennie.db`: banco de dados SQLite utilizado durante o desenvolvimento.
- `index.html`: interface principal da aplicação.
- `index-backup.html`: cópia de segurança da interface original.
- `teste_api.py`: script utilizado para testar o cadastro de despesas pela API.
- `.venv/`: ambiente virtual Python com as dependências do projeto.

A estrutura poderá ser reorganizada conforme o desenvolvimento avançar.

## 5. Backend e banco de dados

O backend está sendo desenvolvido em Python com Flask, enquanto o SQLite é utilizado para armazenar os dados durante a fase de desenvolvimento.

A tabela `despesas` possui os seguintes campos:

| Campo | Descrição |
|---|---|
| `id` | Identificador único da despesa |
| `descricao` | Descrição da despesa |
| `valor` | Valor monetário |
| `data` | Data da despesa |
| `categoria` | Categoria da despesa |

A API disponibiliza, nesta etapa, os seguintes endpoints:

| Método | Endpoint | Função |
|---|---|---|
| GET | `/api/despesas` | Consultar despesas cadastradas |
| POST | `/api/despesas` | Cadastrar uma nova despesa |

A API também realiza validações básicas dos dados enviados antes de efetuar o cadastro.

## 6. Funcionalidades implementadas

- Interface inicial da aplicação.
- Configuração do ambiente de desenvolvimento Python.
- Servidor backend utilizando Flask.
- Criação do banco de dados SQLite.
- Criação da tabela de despesas.
- Endpoint para consulta de despesas.
- Endpoint para cadastro de despesas.
- Validação básica dos dados recebidos pela API.
- Teste de cadastro de despesa com resposta HTTP `201 Created`.

## 7. Funcionalidades em desenvolvimento

- Integração completa entre a interface e o backend.
- Sincronização da listagem de despesas com o banco de dados.
- Implementação de autenticação e gerenciamento de usuários.
- Separação e proteção dos dados de cada usuário.
- Expansão das funcionalidades de controle financeiro.
- Testes automatizados.
- Adaptação e preparação da aplicação para instalação em dispositivos Android.
- Revisão de validações, segurança e experiência de uso.

## 8. Como executar o projeto

### Pré-requisitos

- Python instalado.
- Visual Studio Code ou outro editor de código.
- Git, caso o projeto seja clonado do GitHub.

### Instalação

Clone o repositório:

```bash
git clone https://github.com/m4riaeduarda-dev/plennie.git
```

Entre na pasta do projeto:

```bash
cd plennie
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Instale o Flask:

```bash
.venv\Scripts\python.exe -m pip install Flask
```

Prepare o banco de dados:

```bash
.venv\Scripts\python.exe database.py
```

Inicie o servidor:

```bash
.venv\Scripts\python.exe app.py
```

Após iniciar o servidor, acesse `http://127.0.0.1:5000` no navegador, desde que a rota inicial esteja configurada para disponibilizar a interface HTML.

**Observação:** os comandos acima são destinados ao desenvolvimento em Windows. A configuração da rota inicial e a integração da interface com a API devem estar concluídas para que todas as etapas funcionem como esperado.

## 9. Testes

Foi realizado um teste manual de cadastro de despesa utilizando o script `teste_api.py`. A API retornou o status HTTP `201 Created`, indicando que a solicitação de cadastro foi aceita e processada com sucesso.

Os testes automatizados e a cobertura das demais funcionalidades ainda precisam ser desenvolvidos.

## 10. Segurança e limitações atuais

O projeto encontra-se em fase de desenvolvimento acadêmico. A implementação atual da API ainda não possui autenticação de usuários nem isolamento de dados por conta.

Por esse motivo, a aplicação não deve ser disponibilizada publicamente nem utilizada para armazenar informações financeiras reais antes da implementação e verificação dos mecanismos de segurança necessários.

## 11. Próximas etapas

1. Concluir a integração entre a interface e a API.
2. Garantir que as despesas sejam consultadas diretamente no banco de dados.
3. Implementar autenticação e autorização.
4. Ampliar os testes e as validações.
5. Revisar a interface para dispositivos móveis.
6. Definir e implementar a estratégia de empacotamento e instalação para Android.
7. Atualizar a documentação conforme novas funcionalidades forem concluídas.

## 12. Status do projeto

**Em desenvolvimento.**

O Plennie já possui uma interface inicial, uma estrutura de backend com Flask e um banco de dados SQLite preparado para o cadastro e a consulta de despesas. As próximas etapas concentram-se na integração completa dos componentes, na segurança dos dados e na preparação para utilização em dispositivos Android.

## 13. Equipe

Projeto acadêmico desenvolvido em equipe como parte das atividades do curso de Análise e Desenvolvimento de Sistemas.