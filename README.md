# Projeto Aplicado - Práticas de Mercado: Aplicação Flask Segura com Docker

Este repositório contém o código-fonte, a documentação e os artefatos de um protótipo web desenvolvido sob o conceito de *Secure by Design*, estruturado com autenticação e conteinerizado via Docker.

---

## O que Já Foi Feito (Até o Momento)

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

## Como Executar o Projeto Localmente

### Pré-requisitos
- Ter o **Docker Desktop** instalado e em execução no sistema.

### Passos para Execução:
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/adryeleconceicao-cloud/projeto-aplicado-praticas-mercado.git
   cd projeto-aplicado-praticas-mercado

---

## Arquitetura de Produção e Infraestrutura (Docker Compose & Nginx)

Para simular um ambiente de produção real e seguro, a aplicação foi estruturada utilizando **Docker Compose** integrando dois serviços principais isolados em rede própria:

1. **Servidor Web / Proxy Reverso (Nginx):**
   - Atua na porta padrão **80**, recebendo as requisições externas dos usuários.
   - Realiza o encaminhamento seguro do tráfego (*proxy_pass*) para a aplicação interna, além de adicionar cabeçalhos de controle de IP e protocolo (`X-Real-IP`, `X-Forwarded-For`).

2. **Aplicação Web (Flask + Gunicorn):**
   - Executada de forma isolada dentro de um contêiner baseado em Python `3.11-slim`.
   - Utiliza o **Gunicorn** como servidor WSGI de alta performance para gerenciar as requisições simultâneas com estabilidade.

### Como Executar o Ambiente Completo (Com Nginx):
Certifique-se de que o Docker Desktop está em execução e utilize o comando de orquestração na raiz do projeto:

```bash
docker compose up --build -d

---

## Mitigações de Segurança (OWASP Top 10)

Em conformidade com os conceitos de *Secure by Design* e *Secure by Default*, o protótipo web foi estruturado para mitigar ativamente falhas de segurança comuns mapeadas no **OWASP Top 10**. Abaixo estão descritas as 3 principais mitigações implementadas no código:

### 1. Falhas de Identificação e Autenticação (Authentication Failures)
* **O que é:** Ocorre quando funções de autenticação ou gerenciamento de sessão são implementadas incorretamente, permitindo que atacantes comprometam senhas ou realizem enumeração de usuários.
* **Como foi mitigado no projeto:** Na rota de autenticação (`app.py`), o sistema foi programado para retornar mensagens de erro genéricas e padronizadas (`"Credenciais inválidas!"`), independentemente de o erro ter ocorrido no e-mail/usuário ou na senha. 
* **Onde encontrar no código:** Na função de tratamento de login dentro de `app.py`, onde a validação de credenciais impede o vazamento de informações sobre quais contas de usuário existem de fato no sistema.

### 2. Controle de Acesso Quebrado (Broken Access Control)
* **O que é:** Acontece quando as restrições sobre o que usuários autenticados podem fazer não são aplicadas corretamente, permitindo que atacantes visualizem ou operem funcionalidades não autorizadas (como acessar painéis administrativos sem permissão).
* **Como foi mitigado no projeto:** O painel interno da aplicação (`dashboard.html`) é protegido por rotas restritas no Flask. O acesso só é liberado mediante a verificação de sessão ativa do usuário. Caso contrário, o sistema bloqueia a visualização e redireciona o fluxo de volta para a tela de login.
* **Onde encontrar no código:** Nas diretrizes de rotas protegidas em `app.py`, que exigem validação de sessão antes de renderizar o template do painel interno.

### 3. Injeção (Injection - Tratamento de Entradas)
* **O que é:** Ocorre quando dados não confiáveis são enviados para um interpretador como parte de uma consulta ou comando, permitindo a execução de códigos maliciosos ou burlar a lógica da aplicação.
* **Como foi mitigado no projeto:** O uso estruturado do framework Flask (através do manuseio seguro de requisições via `request.form`) em conjunto com a arquitetura do protótipo garante que as entradas dos usuários sejam tratadas de forma controlada, prevenindo a execução de inputs maliciosos diretamente nos campos de submissão.
* **Onde encontrar no código:** No gerenciamento de formulários HTML em `login.html` e na captura segura de dados realizada no backend (`app.py`).

