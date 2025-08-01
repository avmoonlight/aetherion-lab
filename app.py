from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pymysql
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'segredo'

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
        login = request.form['login']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = %s AND senha = %s", (login, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['nome'] = user.get('nome', 'Usuário')
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
        login = request.form['login']
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
        cursor.execute("INSERT INTO usuarios (nome, login, senha, foto) VALUES (%s, %s, %s, %s)", (nome, login, senha, caminho_foto))
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

    return render_template('novo_relatorio.html', projeto_id=projeto_id)

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'user_id' not in session or not session.get('is_superuser'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        senha = request.form['senha']

        foto = request.files.get('foto')
        caminho_foto = usuario['foto']  # mantém a foto antiga se nenhuma nova for enviada
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            foto.save(caminho_foto)
            caminho_foto = caminho_foto.replace('static/', '')

        cursor.execute("""
            UPDATE usuarios SET nome=%s, login=%s, senha=%s, foto=%s WHERE id=%s
        """, (nome, login, senha, caminho_foto, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    conn.close()
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/editar_projeto/<int:id>', methods=['GET', 'POST'])
def editar_projeto(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos WHERE id = %s", (id,))
    projeto = cursor.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']

        imagem = request.files.get('imagem')
        caminho_imagem = projeto['imagem']
        if imagem and imagem.filename:
            filename = secure_filename(imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            imagem.save(caminho_imagem)
            caminho_imagem = caminho_imagem.replace('static/', '')

        cursor.execute("""
            UPDATE projetos SET nome=%s, descricao=%s, imagem=%s WHERE id=%s
        """, (nome, descricao, caminho_imagem, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('editar_projeto.html', projeto=projeto)

@app.route('/excluir_projeto/<int:id>')
def excluir_projeto(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projetos WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/editar_relatorio/<int:relatorio_id>', methods=['GET', 'POST'])
def editar_relatorio(relatorio_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relatorios WHERE id = %s", (relatorio_id,))
    relatorio = cursor.fetchone()

    if not relatorio:
        flash('Relatório não encontrado.')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        arquivo = request.files.get('arquivo')
        caminho_arquivo = relatorio['arquivo']

        if arquivo and arquivo.filename:
            filename = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            arquivo.save(caminho_arquivo)
            caminho_arquivo = caminho_arquivo.replace('static/', '')

        cursor.execute("UPDATE relatorios SET titulo=%s, arquivo=%s WHERE id=%s",
                       (titulo, caminho_arquivo, relatorio_id))
        conn.commit()
        conn.close()
        return redirect(url_for('projeto', projeto_id=relatorio['projeto_id']))

    conn.close()
    return render_template('editar_relatorio.html', relatorio=relatorio)

@app.route('/excluir_relatorio/<int:relatorio_id>')
def excluir_relatorio(relatorio_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT projeto_id FROM relatorios WHERE id = %s", (relatorio_id,))
    relatorio = cursor.fetchone()

    if relatorio:
        projeto_id = relatorio['projeto_id']
        cursor.execute("DELETE FROM relatorios WHERE id = %s", (relatorio_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('projeto', projeto_id=projeto_id))

    conn.close()
    flash('Relatório não encontrado.')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
