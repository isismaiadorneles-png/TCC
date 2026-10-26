from flask import Flask, render_template, request, redirect, session, make_response, jsonify
import mysql.connector
import os
import json

app = Flask(__name__)

def get_db_connection():#aqui esta a função usada nas conexoes com o banco de dados
    """Função auxiliar para conectar ao banco de dados MySQL."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'TCC')
    )

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/loginusuario', methods=['GET', 'POST'])
@app.route('/loginusuario.html', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':#Esse comando diz= "se ocorrer o metodo post executar:"
        #o metodo .get() é usado de forma segura para evitar erro caso o campo nao seja preechido 
        nome = request.form.get('nome')#pega o valor que foi colocado no placeholder
        senha = request.form.get('senha')#aqui faz a mesma coisa da linha anterior mas pegando valor da senha 
        conexao = get_db_connection()#chama a função que conecta com o banco de dados

        cursor = conexao.cursor()#usado para executar comandos la no banco de dados em sql
        query = "SELECT id FROM funcionario WHERE nome = %s AND senha = %s"
        #Esta query define uma consulta que deve ser feita no banco de dados a tabela funcionarios, onde tem nome e senha e ele pede para verificar se as respostas fornecidas nos placeholders é a mesma informação que esta no banco de dados para liberar espaço
        cursor.execute(query, (nome, senha))#Aqui ele executa a consulta que foi definida, tipo um chefe definindo oq o funcionario tem que fazer, essa linha é o funcionario e anterior é o chefe
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        if resultado:
            session['usuario_logado'] = nome
            return redirect('/estoque.html')
        else:
            return render_template("loginusuario.html", erro=True)

    return render_template("loginusuario.html")

@app.route('/estoque', methods=['GET', 'POST'])#aqui tem que revisar as anotações e expçlicações do que é cada coisa
@app.route('/estoque.html', methods=['GET', 'POST'])
def estoque():
    if 'usuario_logado' not in session:
        return redirect('/loginusuario.html')
    conexao = get_db_connection()

    cursor = conexao.cursor()
    query = "SELECT id, nome, quantidade, estoque_minimo, descrição, preço, categoria, imagem FROM estoque_almoxarifado"
    print("foi")

    cursor.execute(query)
    resultado_banco = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template("estoque.html", resultado=resultado_banco)

@app.route('/historico')#aqui precisa revisaar as anotações
@app.route('/historico.html')
def historico():
    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM historico")
    todas_retiradas = cursor.fetchall()
    
    cursor.close()
    conexao.close()
    
    return render_template("historico.html", retiradas=todas_retiradas)

app = Flask(__name__)
app.config['JSON_SORT_KERYS'] = False

@app.route('/criacaoItem', methods=['GET', 'POST'])
@app.route('/criacaoItem.html', methods=['GET', 'POST'])
def criacao_item():
 if request.method == 'POST':
    conexao = get_db_connection()#aqui é para conexao com banco de dados
    print('teste se metodo = post')#aqui é só pra confirmar que ta rodando o codigo
    dado_name = request.form['nome']
    dado_funcao = request.form['funcao']
    dado_senha = request.form['senha']
    
    cursor = conexao.cursor()#cursor serve pra fazer conexao com o banco de dados por comandos emm sql
    #"query" é consulta, é um comando  para ele consultar qualquer tipo de informação envolvendo o banco de dados desde de busacar, filtrar, inserirr e atualizar os dados enviados ao banco
    query = """
    INSERT INTO funcionario (nome, funcao, senha)
    VALUES (%s, %s, %s)
    """#esse trecho da linha 59 ate 61 esta dizendo sobre os lugares que vao ter informações inseridas e os % sao como placeholder, ou seja que ha espaço para inserir os dados
    valores = (dado_name, dado_funcao, dado_senha)#aqui ele vai armazenar os dados que vao ser inseridos nos nomes, função e senha, esse tipo de comando é uma tupla
    
    cursor.execute(query, valores)#aqui ele vai executar os comandos, vai pegar o "valores" que há a tupla dentro e vai substituir os % que tem no banco e colocar as informações que a tupla vai ter armazenada
    conexao.commit()#aqui ele confirma
    
    cursor.close()
    conexao.close()

    return render_template("criacaoItem.html")

@app.route('/solicitar', methods=['GET', 'POST'])#precisa rever as anotações
@app.route('/solicitar.html', methods=['GET', 'POST'])
def solicitar():
    if request.method == 'POST':
        conexao = get_db_connection()
        cursor = conexao.cursor()

        dado_id = request.form['id']
        dado_quantidade = int(request.form['quantidade'])
        acao = request.form['acao']

        cursor.execute("SELECT quantidade FROM estoque_almoxarifado WHERE id = %s", (dado_id,))

        resultado = cursor.fetchone()
        if resultado:
            quantidade_atual = int(resultado[0]) if (resultado[0] is not None and str(resultado[0]).isdigit()) else 0
            if acao == 'colocar':
                nova_quantidade = quantidade_atual + dado_quantidade
            elif acao == 'retirar':
                if quantidade_atual >= dado_quantidade:
                    nova_quantidade = quantidade_atual - dado_quantidade
                else:
                    nova_quantidade = 0
            else:
                nova_quantidade = quantidade_atual

            cursor.execute("""
                UPDATE estoque_almoxarifado
                SET quantidade = %s
                WHERE id = %s
            """, (nova_quantidade, dado_id))

            cursor.execute("SELECT nome FROM estoque_almoxarifado WHERE id = %s", (dado_id,))
            produto = cursor.fetchone()
            
            if produto:
                nome_produto = produto[0]
                sql_historico = "INSERT INTO historico (nome, quantidade, acao) VALUES (%s, %s, %s)"
                cursor.execute(sql_historico, (nome_produto, dado_quantidade, acao))

        conexao.commit()
        cursor.close()
        conexao.close()
        
    return render_template("solicitar.html")

@app.route('/tabela')#aqui nao precisa de methods
@app.route('/tabela.html')#aqui precisa ser revisado as anotações e oq é cada coisa
def tabela():
    conexao = get_db_connection()

    cursor = conexao.cursor()
    query = "SELECT id, nome, funcao, senha FROM funcionario"
    print("foi")

    cursor.execute(query)
    resultado_banco = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template("tabela.html", resultado=resultado_banco)

@app.route('/criacaoUser', methods=['GET', 'POST'])#precisa ser revisado e anotar oq é cada coisa
@app.route('/criacaoUser.html', methods=['GET', 'POST'])
def criacao():
    if request.method == 'POST':
        conexao = get_db_connection()
        print('teste se metodo = post')
        dado_name = request.form['nome']
        dado_funcao = request.form['funcao']
        dado_senha = request.form['senha']

        cursor = conexao.cursor()
        query = """
        INSERT INTO funcionario (nome, funcao, senha)
        VALUES (%s, %s, %s)
        """
        valores = (dado_name, dado_funcao, dado_senha)

        cursor.execute(query, valores)
        conexao.commit()

        cursor.close()
        conexao.close()
   
    return render_template("criacao.html")

# --- Assistente virtual (adicionado) ---
from assistente import init_assistente
init_assistente(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)