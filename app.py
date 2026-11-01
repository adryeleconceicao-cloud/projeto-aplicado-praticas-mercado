"""
Protótipo web seguro (Flask) - Projeto Aplicado: Práticas de Mercado.

Mitigações da OWASP Top 10:2025 implementadas neste arquivo:

1. Authentication Failures
   - Senha armazenada apenas como hash (scrypt, via Werkzeug); nunca em texto puro.
   - Mensagem de erro genérica (não revela se o usuário ou a senha estava errado).
   - Limite de tentativas de login por IP (bloqueio temporário).
   - Sessão renovada no login (session.clear) e encerrada por completo no logout.
   - Cookie de sessão com HttpOnly, Secure e SameSite, e expiração por tempo.

2. Broken Access Control
   - Todas as rotas internas passam pelo decorador @login_obrigatorio.
   - Sem sessão válida, o acesso é redirecionado para a tela de login.
   - Páginas autenticadas enviadas com Cache-Control: no-store (o botão "voltar"
     do navegador não reexibe o painel depois do logout).

3. Security Misconfiguration
   - Nenhum segredo no código: usuário, hash da senha e SECRET_KEY vêm de variáveis
     de ambiente, e o app se recusa a iniciar se alguma estiver ausente.
   - debug desativado; servidor local escuta só em 127.0.0.1 por padrão.
   - Cabeçalhos de segurança (CSP, X-Frame-Options, X-Content-Type-Options,
     Referrer-Policy).
   - Tamanho máximo de requisição e das entradas do formulário.
"""

import hmac
import os
import time
from collections import defaultdict, deque
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash


# ---------------------------------------------------------------------------
# Configuração (Security Misconfiguration)
# ---------------------------------------------------------------------------

def _variavel_obrigatoria(nome):
    """Lê uma variável de ambiente; sem valor padrão, o app não sobe sem ela."""
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {nome}")
    return valor


app = Flask(__name__)

app.secret_key = _variavel_obrigatoria("SECRET_KEY")
USUARIO_VALIDO = _variavel_obrigatoria("APP_USER")
SENHA_HASH = _variavel_obrigatoria("APP_PASSWORD_HASH")

# O app roda atrás de 1 proxy (Nginx). Isso faz o Flask enxergar o IP real do
# cliente (X-Forwarded-For) e o protocolo HTTPS (X-Forwarded-Proto).
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Em produção (HTTPS) o cookie só trafega criptografado. Para testar em
    # http://127.0.0.1 localmente, defina COOKIE_SECURE=false.
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "true").lower() != "false",
    PERMANENT_SESSION_LIFETIME=1800,  # sessão expira em 30 minutos
    MAX_CONTENT_LENGTH=16 * 1024,     # recusa requisições maiores que 16 KB
)

TAMANHO_MAXIMO_CAMPO = 128


# ---------------------------------------------------------------------------
# Limite de tentativas de login (Authentication Failures)
# ---------------------------------------------------------------------------

MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 300  # 5 minutos

_falhas_por_ip = defaultdict(deque)


def _purgar_expirados():
    agora = time.time()
    for ip in list(_falhas_por_ip):
        fila = _falhas_por_ip[ip]
        while fila and agora - fila[0] > JANELA_SEGUNDOS:
            fila.popleft()
        if not fila:
            del _falhas_por_ip[ip]


def _ip_bloqueado(ip):
    fila = _falhas_por_ip.get(ip)
    if not fila:
        return False
    agora = time.time()
    while fila and agora - fila[0] > JANELA_SEGUNDOS:
        fila.popleft()
    if not fila:
        del _falhas_por_ip[ip]
        return False
    return len(fila) >= MAX_TENTATIVAS


def _registrar_falha(ip):
    if len(_falhas_por_ip) > 5000:
        _purgar_expirados()
    _falhas_por_ip[ip].append(time.time())


# ---------------------------------------------------------------------------
# Autenticação e controle de acesso
# ---------------------------------------------------------------------------

def credenciais_validas(usuario, senha):
    """Confere usuário e senha sem vazar qual dos dois estava errado.

    O hash da senha é sempre verificado, mesmo quando o usuário está errado, para
    que o tempo de resposta seja parecido nos dois casos.
    """
    usuario_ok = hmac.compare_digest(
        usuario.encode("utf-8"), USUARIO_VALIDO.encode("utf-8")
    )
    senha_ok = check_password_hash(SENHA_HASH, senha)
    return usuario_ok and senha_ok


def login_obrigatorio(rota):
    """Broken Access Control: só deixa passar quem tem sessão autenticada."""
    @wraps(rota)
    def protegida(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return rota(*args, **kwargs)
    return protegida


@app.after_request
def cabecalhos_de_seguranca(resposta):
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    resposta.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    )
    resposta.headers["Cache-Control"] = "no-store"
    return resposta


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        ip = request.remote_addr or "desconhecido"

        if _ip_bloqueado(ip):
            app.logger.warning("Login bloqueado por excesso de tentativas: ip=%s", ip)
            erro = "Muitas tentativas. Aguarde alguns minutos e tente novamente."
            return render_template("login.html", erro=erro), 429

        usuario = request.form.get("username", "").strip()
        senha = request.form.get("password", "")

        entrada_valida = (
            len(usuario) <= TAMANHO_MAXIMO_CAMPO and len(senha) <= TAMANHO_MAXIMO_CAMPO
        )

        if entrada_valida and credenciais_validas(usuario, senha):
            session.clear()  # nova sessão a cada login
            session["usuario"] = USUARIO_VALIDO
            session.permanent = True
            _falhas_por_ip.pop(ip, None)
            app.logger.info("Login realizado: ip=%s", ip)
            return redirect(url_for("dashboard"))

        _registrar_falha(ip)
        app.logger.warning("Falha de login: ip=%s", ip)
        erro = "Credenciais inválidas!"

    return render_template("login.html", erro=erro)


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    return render_template("dashboard.html", usuario=session["usuario"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Uso local apenas. Em produção o app roda com Gunicorn atrás do Nginx.
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=5000, debug=False)