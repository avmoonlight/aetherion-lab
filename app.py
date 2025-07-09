from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pymysql
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configurações do MySQL
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'atherion'

# Pasta de upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['nome'] = user['nome']
            session['is_superuser'] = user['id'] == 1
            if session['is_superuser']:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
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
    return render_template('dashboard.html', projetos=projetos, nome=session['nome'])


@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_superuser'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('admin.html', usuarios=usuarios)


@app.route('/novo_usuario', methods=['GET', 'POST'])
def novo_usuario():
    if 'user_id' not in session or not session.get('is_superuser'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        foto = request.files.get('foto')
        caminho_foto = ''
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            foto.save(caminho_foto)
            caminho_foto = caminho_foto.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha, foto) VALUES (%s, %s, %s, %s)", (nome, email, senha, caminho_foto))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    return render_template('novo_usuario.html')


@app.route('/excluir_usuario/<int:id>')
def excluir_usuario(id):
    if 'user_id' not in session or not session.get('is_superuser'):
        return redirect(url_for('login'))

    if id == 1:
        flash('Não é possível excluir o superuser.')
        return redirect(url_for('admin'))

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

        imagem = request.files.get('imagem')
        caminho_imagem = ''
        if imagem and imagem.filename:
            filename = secure_filename(imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            imagem.save(caminho_imagem)
            caminho_imagem = caminho_imagem.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projetos (nome, descricao, imagem) VALUES (%s, %s, %s)", (nome, descricao, caminho_imagem))
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

        arquivo = request.files.get('arquivo')
        caminho_arquivo = ''
        if arquivo and arquivo.filename:
            filename = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            arquivo.save(caminho_arquivo)
            caminho_arquivo = caminho_arquivo.replace('static/', '')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO relatorios (projeto_id, titulo, arquivo) VALUES (%s, %s, %s)", (projeto_id, titulo, caminho_arquivo))
        conn.commit()
        conn.close()
        return redirect(url_for('projeto', projeto_id=projeto_id))

    return render_template('novo_relatorio.html')


if __name__ == '__main__':
    app.run(debug=True)
