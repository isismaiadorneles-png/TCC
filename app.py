from flask import Flask, render_template, request, redirect, session, make_response, jsonify, flash
from flask_bcrypt import Bcrypt
import mysql.connector
import os
import json
from functools import wraps
from werkzeug.utils import secure_filename
        
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Tccnota10')

PASTA_IMAGENS = os.path.join(app.root_path, 'static', 'imagens_produtos')

def get_db_connection():#Função para conectar com o banco de dados
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'TCC')
    )

def gerar_hash(senha):#Função para as senhas com hash
    return bcrypt.generate_password_hash(senha).decode('utf-8')

def senha_confirmada(senha_digitada, hash_do_banco):#Função para senhas com hash
    return bcrypt.check_password_hash(hash_do_banco, senha_digitada)
#abaixo tem funções para proteção de rotas
def login_required(funcao):#aqui proteção no login
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if "tipo" not in session:
            return redirect("/index.html")
        return funcao(*args, **kwargs)
    return wrapper

def admin_required(funcao):#aqui proteção para admin
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if "tipo" not in session:
            return redirect("/index.html")
        if session["tipo"] != "admin":
            return redirect("/estoque.html")
        return funcao(*args, **kwargs)
    return wrapper

def autenticar(nome, senha, tipo_esperado):
    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)  # dictionary=True -> usuario["senha"] funciona
    cursor.execute(
        "SELECT * FROM usuario WHERE nome = %s AND tipo = %s",
        (nome, tipo_esperado)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()
 
    if usuario and senha_confirmada(senha, usuario["senha"]):
        session["nome"] = usuario["nome"]
        session["tipo"] = usuario["tipo"]
        return True
    return False

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():  # tela do ADMIN
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        if autenticar(nome, senha, "admin"):
            return redirect("/estoque.html")
        flash("Nome ou senha incorretos")
    return render_template("login.html")

@app.route('/loginusuario', methods=['GET', 'POST'])
@app.route('/loginusuario.html', methods=['GET', 'POST'])
def login_usuario():  # tela do USUÁRIO
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        if autenticar(nome, senha, "usuario"):
            return redirect("/estoque.html")
        flash("Nome ou senha incorretos")
    return render_template("loginusuario.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/index.html")

@app.route('/estoque')
@app.route('/estoque.html')
@login_required
def estoque():
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, nome, quantidade, estoque_minimo, descrição, preço, categoria, imagem "
        "FROM estoque_almoxarifado"
    )
    resultado_banco = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("estoque.html", resultado=resultado_banco)

@app.route('/historico')
@app.route('/historico.html')
@login_required
def historico():
    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM historico")
    todas_retiradas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("historico.html", retiradas=todas_retiradas)


app.config['JSON_SORT_KERYS'] = False

@app.route('/criacaoItem', methods=['GET', 'POST'])
@app.route('/criacaoItem.html', methods=['GET', 'POST'])
@admin_required
def criacao_item():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        categoria = request.form['categoria']
        estoque_minimo = request.form['estoque_minimo']
        descricao = request.form['descrição']
        preco = request.form['preço']
 
        # imagem: salva o arquivo na pasta static/imagens_produtos
        nome_imagem = ""
        arquivo = request.files.get('imagem')
        if arquivo and arquivo.filename:
            nome_imagem = secure_filename(arquivo.filename)
            os.makedirs(PASTA_IMAGENS, exist_ok=True)
            arquivo.save(os.path.join(PASTA_IMAGENS, nome_imagem))
 
        conexao = get_db_connection()
        cursor = conexao.cursor()
        cursor.execute(
            """INSERT INTO estoque_almoxarifado
               (nome, quantidade, estoque_minimo, descrição, preço, categoria, imagem)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (nome, quantidade, estoque_minimo, descricao, preco, categoria, nome_imagem)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
 
    return render_template("criacaoItem.html")

@app.route('/solicitar', methods=['GET', 'POST'])
@app.route('/solicitar.html', methods=['GET', 'POST'])
@login_required
def solicitar():
    if request.method == 'POST':
        conexao = get_db_connection()
        cursor = conexao.cursor()
 
        dado_id = request.form['id']
        dado_quantidade = int(request.form['quantidade'])
        acao = request.form['acao']
 
        cursor.execute("SELECT nome, quantidade FROM estoque_almoxarifado WHERE id = %s", (dado_id,))
        produto = cursor.fetchone()
 
        if produto:
            nome_produto, qtd = produto
            quantidade_atual = int(qtd) if (qtd is not None and str(qtd).isdigit()) else 0
 
            if acao == 'colocar':
                nova_quantidade = quantidade_atual + dado_quantidade
            elif acao == 'retirar':
                nova_quantidade = max(quantidade_atual - dado_quantidade, 0)
            else:
                nova_quantidade = quantidade_atual
 
            cursor.execute(
                "UPDATE estoque_almoxarifado SET quantidade = %s WHERE id = %s",
                (nova_quantidade, dado_id)
            )
            cursor.execute(
                "INSERT INTO historico (nome, quantidade, acao) VALUES (%s, %s, %s)",
                (nome_produto, dado_quantidade, acao)
            )
 
        conexao.commit()
        cursor.close()
        conexao.close()
 
    return render_template("solicitar.html")

@app.route('/tabela')
@app.route('/tabela.html')
@admin_required
def tabela():
    conexao = get_db_connection()
    cursor = conexao.cursor()
    # não existe coluna "funcao" na tabela usuario; é "tipo". E não mostramos o hash.
    cursor.execute("SELECT id, nome, tipo FROM usuario")
    resultado_banco = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("tabela.html", resultado=resultado_banco)

@app.route('/criacaoUser', methods=['GET', 'POST'])
@app.route('/criacaoUser.html', methods=['GET', 'POST'])
@admin_required
def criacao():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        tipo = request.form['tipo']          # 'admin' ou 'usuario'
 
        if tipo not in ('admin', 'usuario'):
            flash("Tipo inválido")
            return render_template("criacaoUser.html")
 
        senha_hash = gerar_hash(senha)       # NUNCA salve a senha pura
 
        conexao = get_db_connection()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuario (nome, senha, tipo) VALUES (%s, %s, %s)",
            (nome, senha_hash, tipo)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Usuário criado com sucesso")
 
    return render_template("criacaoUser.html")

def criar_admin_padrao():
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM usuario WHERE tipo = 'admin' LIMIT 1")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO usuario (nome, senha, tipo) VALUES (%s, %s, %s)",
            ("administrador", gerar_hash("1000"), "admin")
        )
        conexao.commit()
        print("Admin padrão criado: administrador / 1000")
    cursor.close()
    conexao.close()

if __name__ == '__main__':
    try:
        criar_admin_padrao()
    except Exception as erro:
        print("Não foi possível criar o admin padrão:", erro)
    app.run(host='0.0.0.0', port=5000, debug=True)
