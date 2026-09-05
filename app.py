from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura_para_sessao'

USUARIO_VALIDO = "admin"
SENHA_VALIDA = "seguranca2026"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('username', '').strip()
        senha = request.form.get('password', '').strip()
        
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            erro = "Credenciais inválidas!"
            
    return render_template('login.html', erro=erro)

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)