from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
import mysql.connector
import os
from functools import wraps
from werkzeug.utils import secure_filename
        
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Tccnota10')

PASTA_IMAGENS = os.path.join(app.root_path, 'static', 'imagens_produtos')


class RowObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def get_db_connection():
    conexao = mysql.connector.connect(
        host='db_almox',
        user='root',
        password='root',
        database='TCC',
        buffered=True  
    )
    
    cursor = conexao.cursor(buffered=True) 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_almoxarifado (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        quantidade INT NOT NULL DEFAULT 0,
        estoque_minimo INT NOT NULL DEFAULT 0,
        descricao TEXT,
        descrição TEXT,
        preco DECIMAL(10,2) DEFAULT 0.00,
        preço DECIMAL(10,2) DEFAULT 0.00,
        categoria VARCHAR(255),
        imagem VARCHAR(255)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL,
        tipo ENUM('admin', 'usuario') NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentaçoes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        item_id INT NOT NULL,
        tipo ENUM('ADICIONAR', 'RETIRAR') NOT NULL,
        quantidade INT NOT NULL,
        responsavel VARCHAR(100),
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES estoque_almoxarifado(id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255),
        quantidade INT NOT NULL,
        acao VARCHAR(255)
    );
    """)
    
    senha_correta_hash = bcrypt.generate_password_hash('1000').decode('utf-8')
    cursor.execute("""
    REPLACE INTO usuario (id, nome, senha, tipo) 
    VALUES (1, 'administrador', %s, 'admin');
    """, (senha_correta_hash,))
    
    conexao.commit()
    
    
    while cursor.nextset():
        pass
        
    cursor.close()
    return conexao

def gerar_hash(senha):
    return bcrypt.generate_password_hash(senha).decode('utf-8')

def senha_confirmada(senha_digitada, hash_do_banco):
    return bcrypt.check_password_hash(hash_do_banco, senha_digitada)

def login_required(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if "tipo" not in session:
            return redirect("/index.html")
        return funcao(*args, **kwargs)
    return wrapper

def admin_required(funcao):
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
    cursor = conexao.cursor(dictionary=True)
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
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        if autenticar(nome, senha, "admin"):
            return redirect("/estoque.html")
        flash("Nome ou senha incorretos")
    return render_template("login.html")

@app.route('/loginusuario', methods=['GET', 'POST'])
@app.route('/loginusuario.html', methods=['GET', 'POST'])
def login_usuario():
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
        "SELECT id, nome, quantidade, estoque_minimo, descricao, preço, categoria, imagem "
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
    cursor.execute("SELECT id, nome, quantidade, acao FROM historico ORDER BY id DESC")
    linhas_banco = cursor.fetchall()
    cursor.close()
    conexao.close()
    
   
    lista_objetos = [RowObject(**linha) for linha in linhas_banco]
    return render_template("historico.html", retiradas=lista_objetos)

@app.route('/criacaoItem', methods=['GET', 'POST'])
@app.route('/criacaoItem.html', methods=['GET', 'POST'])
@login_required     
def criacao_item():
    if request.method == 'POST':
        nome = request.form.get('nome')
        quantidade = request.form.get('quantidade')
        categoria = request.form.get('categoria')
        estoque_minimo = request.form.get('estoque_minimo')
 
        descricao = request.form.get('descrição') or request.form.get('descricao') or ""
        preco = request.form.get('preço') or request.form.get('preco') or "0.00"
 
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
               (nome, quantidade, estoque_minimo, descricao, descrição, preco, preço, categoria, imagem)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (nome, quantidade, estoque_minimo, descricao, descricao, preco, preco, categoria, nome_imagem)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Item cadastrado com sucesso!")
    return render_template("criacaoItem.html")

@app.route('/solicitar', methods=['GET', 'POST'])
@app.route('/solicitar.html', methods=['GET', 'POST'])
@login_required
def solicitar():
    if request.method == 'POST':
        print("\n=== O BOTAO FOI CLICADO! REQUISICAO RECEBIDA ===", flush=True)
        print(f"Dados que sairam do HTML: {request.form}", flush=True)
        print("================================================\n", flush=True)
        conexao = get_db_connection()
        cursor = conexao.cursor()
 
        nome_desejado = request.form.get('Itens') or request.form.get('itens') or request.form.get('item') or request.form.get('produto') or request.form.get('nome')
        dado_quantidade_raw = request.form.get('quantidade') or request.form.get('qtd') or '0'
        dado_quantidade = int(dado_quantidade_raw) if str(dado_quantidade_raw).isdigit() else 0
        
        form_keys_upper = [k.upper() for k in request.form.keys()]
        form_values_upper = [str(v).upper() for v in request.form.values()]
        
        if 'ENTRADA' in form_keys_upper or 'ENTRADA' in form_values_upper or request.form.get('acao') == 'colocar':
            acao_tipo = 'colocar'
        elif 'SAÍDA' in form_keys_upper or 'SAIDA' in form_keys_upper or 'SAÍDA' in form_values_upper or 'SAIDA' in form_values_upper or request.form.get('acao') == 'retirar':
            acao_tipo = 'retirar'
        else:
            acao_tipo = 'colocar'

        if nome_desejado:
            nome_desejado = nome_desejado.strip()

        cursor.execute("SELECT id, quantidade FROM estoque_almoxarifado WHERE nome = %s", (nome_desejado,))
        produto = cursor.fetchone()
 
        if produto:
            produto_id, qtd = produto
            quantidade_atual = int(qtd) if (qtd is not None and str(qtd).isdigit()) else 0
 
            if acao_tipo == 'colocar':
                nova_quantidade = quantidade_atual + dado_quantidade
                texto_acao = f"Entrada (Adicionado {dado_quantidade} unidades)"
            else:
                nova_quantidade = max(quantidade_atual - dado_quantidade, 0)
                texto_acao = f"Saída (Retirado {dado_quantidade} unidades)"
            cursor.execute(
                "UPDATE estoque_almoxarifado SET quantidade = %s WHERE id = %s",
                (nova_quantidade, produto_id)
            )
            cursor.execute(
                "INSERT INTO historico (nome, quantidade, acao) VALUES (%s, %s, %s)",
                (nome_desejado, dado_quantidade, texto_acao)
            )
            conexao.commit()
            flash("Movimentação realizada com sucesso!")
        else:
            flash(f"Erro: O produto '{nome_desejado}' não foi localizado no estoque.")
 
        cursor.close()
        conexao.close()
 
    return render_template("solicitar.html")

@app.route('/tabela')
@app.route('/tabela.html')
def tabela():
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, tipo FROM usuario")
    resultado_banco = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("tabela.html", resultado=resultado_banco)

@app.route('/criacaoUser', methods=['GET', 'POST'])
@app.route('/criacaoUser.html', methods=['GET', 'POST'])
def criacao():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        tipo = request.form.get('tipo')

        if tipo not in ('admin', 'usuario'):
            flash("Tipo inválido")
            return render_template("criacaoUser.html")

        senha_hash = gerar_hash(senha)

        conexao = get_db_connection()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuario (nome, senha, tipo) VALUES (%s, %s, %s)",

                (nome, senha_hash, tipo)
            )
            conexao.commit()
            flash("Usuário criado com sucesso")
        except mysql.connector.IntegrityError:
            flash("Já existe um usuário com esse nome")
        finally:
            cursor.close()
            conexao.close()

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