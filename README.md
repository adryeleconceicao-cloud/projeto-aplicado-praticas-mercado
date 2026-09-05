# Projeto Aplicado - Práticas de Mercado: Aplicação Flask Segura com Docker

Este repositório contém o código-fonte, a documentação e os artefatos de um protótipo web desenvolvido sob o conceito de *Secure by Design*, estruturado com autenticação e conteinerizado via Docker.

---

##  O que Já Foi Feito (Até o Momento)

### 1. Desenvolvimento do Protótipo Web (Flask)
- **Estrutura da Aplicação (`app.py`):** Configuração do framework Flask contendo as rotas principais (página de login, autenticação e painel interno protegido).
- **Tratamento de Segurança no Login:** Implementação de validação de credenciais que retorna mensagens genéricas ("Credenciais inválidas!") para mitigar riscos de enumeração de usuários.
- **Interfaces (`templates/`):** Criação das telas em HTML (`login.html` e `dashboard.html`) utilizando boas práticas de estilização.
- **Gerenciamento de Dependências (`requirements.txt`):** Listagem das bibliotecas necessárias para o funcionamento do projeto (como o próprio Flask).

### 2. Controle de Versão e Segurança (GitHub)
- **Configuração do Repositório:** Criação de um repositório público no GitHub seguindo as diretrizes de versionamento seguro.
- **Boas Práticas de Prevenção de Vazamento:** Criação do arquivo `.gitignore` para impedir o envio acidental de arquivos sensíveis, caches (`__pycache__/`), ambientes virtuais (`venv/`) ou credenciais locais.

### 3. Conteinerização da Aplicação (Docker)
- **Criação da Imagem (`docker build`):** Empacotamento da aplicação Flask, dependências e interpretador Python em uma imagem isolada chamada `meu-flask-app`.
- **Execução do Contêiner (`docker run`):** Instanciação do contêiner em modo detached (`-d`), realizando o mapeamento de portas (`5000:5000`) para expor o serviço localmente.
- **Validação Local:** Acesso verificado via navegador em `http://localhost:5000/login`, confirmando o correto funcionamento do fluxo de rotas e submissão de formulários.

---

##  Como Executar o Projeto Localmente

### Pré-requisitos
- Ter o **Docker Desktop** instalado e em execução no sistema.

### Passos para Execução:
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/adryeleconceicao-cloud/projeto-aplicado-praticas-mercado.git
   cd projeto-aplicado-praticas-mercado