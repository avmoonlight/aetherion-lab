from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura'

# Configuração do banco — AJUSTADO
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''  # sem senha
MYSQL_DB = 'atherion'  # nome do banco igual ao seu

# Pasta de uploads
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )


# =======================
# ROTAS
# =======================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']

            if user['id'] == 1:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos")
    projetos = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', projetos=projetos, nome=session['user_nome'])


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['user_id'] != 1:
        return "Acesso negado!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    return render_template('admin.html', usuarios=usuarios)


@app.route('/admin/novo_usuario', methods=['GET', 'POST'])
def novo_usuario():
    if 'user_id' not in session or session['user_id'] != 1:
        return "Acesso negado!"

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        foto = request.files['foto']

        senha_hash = generate_password_hash(senha)

        foto_caminho = ''
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            foto.save(caminho)
            foto_caminho = caminho.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha, foto) VALUES (%s, %s, %s, %s)",
                       (nome, email, senha_hash, foto_caminho))
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))

    return render_template('novo_usuario.html')


@app.route('/admin/excluir_usuario/<int:id>')
def excluir_usuario(id):
    if 'user_id' not in session or session['user_id'] != 1:
        return "Acesso negado!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))


@app.route('/novo_projeto', methods=['GET', 'POST'])
def novo_projeto():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        imagem = request.files['imagem']

        imagem_caminho = ''
        if imagem and imagem.filename:
            filename = secure_filename(imagem.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            imagem.save(caminho)
            imagem_caminho = caminho.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projetos (nome, descricao, imagem) VALUES (%s, %s, %s)",
                       (nome, descricao, imagem_caminho))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('novo_projeto.html')


@app.route('/projeto/<int:projeto_id>')
def projeto(projeto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos WHERE id = %s", (projeto_id,))
    projeto = cursor.fetchone()

    cursor.execute("SELECT * FROM relatorios WHERE projeto_id = %s", (projeto_id,))
    relatorios = cursor.fetchall()
    conn.close()

    return render_template('projeto.html', projeto=projeto, relatorios=relatorios)


@app.route('/projeto/<int:projeto_id>/novo_relatorio', methods=['GET', 'POST'])
def novo_relatorio(projeto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        arquivo = request.files['arquivo']

        caminho_relativo = ''
        if arquivo and arquivo.filename:
            filename = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            arquivo.save(caminho)
            caminho_relativo = caminho.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO relatorios (projeto_id, titulo, arquivo) VALUES (%s, %s, %s)",
                       (projeto_id, titulo, caminho_relativo))
        conn.commit()
        conn.close()

        return redirect(url_for('projeto', projeto_id=projeto_id))

    return render_template('novo_relatorio.html', projeto_id=projeto_id)


if __name__ == '__main__':
    app.run(debug=True)
