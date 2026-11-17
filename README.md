# Plennie

Aplicativo web de organização financeira pessoal, desenvolvido como projeto acadêmico do curso de Análise e Desenvolvimento de Sistemas da Faculdade Anhanguera.

## Sobre

O Plennie auxilia usuários na organização de finanças pessoais com interface minimalista em abas, sem conexão bancária. Permite registrar despesas, parcelamentos, metas, eventos e cofrinhos (individuais e coletivos).

## Tecnologias

- **Frontend:** HTML5 + CSS3 + JavaScript (vanilla)
- **Backend:** Python 3 + Flask 3
- **Banco:** SQLite
- **Autenticação:** Werkzeug (hash) + cookie de sessão assinado
- **Versionamento:** Git + GitHub

## Estrutura

plennie/
├── app.py # API Flask (auth + CRUD de despesas)
├── database.py # Conexão e criação de tabelas
├── index.html # Interface (SPA)
├── requirements.txt # Dependências
├── teste_api.py # Teste de integração da API
├── README.md
├── plennie.db # criado ao rodar database.py (não vai para o Git)
├── .secret_key # criado ao rodar app.py (não vai para o Git)
└── .venv/ # ambiente virtual (não vai para o Git)
