from flask import Flask, render_template, request, redirect, url_for, flash, session
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave_secreta"

# --------------------- Conexão com o Banco ---------------------
def ConectarBD():
    try:
        cnx = connect(
            user='root',
            password='1406',
            host='127.0.0.1',
            database='pygreen2'
        )
        return cnx
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def InserirAlterarRemover(sql, dados):
    cnx = ConectarBD()
    if cnx is None:
        return False
    try:
        cursor = cnx.cursor()
        cursor.execute(sql, dados)
        cnx.commit()
        return True
    except Error as e:
        print(f"Erro ao executar comando: {e}")
        return False
    finally:
        cnx.close()

def ConsultarBD(sql, dados=None):
    cnx = ConectarBD()
    if cnx is None:
        return []
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(sql, dados or ())
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao consultar banco: {e}")
        return []
    finally:
        cnx.close()

# --------------------- Rotas ---------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se email já existe
        sql_check = "SELECT id FROM usuarios WHERE email=%s"
        if ConsultarBD(sql_check, (email,)):
            flash("Email já cadastrado!", "danger")
            return redirect(url_for('cadastro'))

        senha_hash = generate_password_hash(senha)
        sql = "INSERT INTO usuarios (nome, telefone, email, senha) VALUES (%s, %s, %s, %s)"
        sucesso = InserirAlterarRemover(sql, (nome, telefone, email, senha_hash))

        if sucesso:
            session['usuario'] = email
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for('niveis'))
        else:
            flash("Erro ao cadastrar!", "danger")
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        sql = "SELECT id, senha FROM usuarios WHERE email=%s"
        resultados = ConsultarBD(sql, (email,))

        if resultados:
            usuario = resultados[0]
            if check_password_hash(usuario['senha'], senha):
                session['usuario'] = email
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('niveis'))

        flash("Email ou senha incorretos!", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Você foi desconectado.", "success")
    return redirect(url_for('login'))

@app.route('/niveis')
def niveis():
    return render_template('niveis.html')

@app.route('/modulo/<int:num>')
def modulo(num):
    if num < 1 or num > 5:
        return "Módulo não encontrado", 404
    return render_template(f'modulo{num}.html', num=num)

# --------------------- Executar ---------------------
if __name__ == '__main__':
    app.run(debug=True)
