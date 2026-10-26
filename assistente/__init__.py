"""
Assistente virtual do Almoxarifado.

Como funciona:
  - Cria a rota POST /assistente/chat (conversa com a IA).
  - Serve o widget em /assistente/static/assistente.js.
  - Injeta o widget automaticamente em TODAS as páginas HTML (antes de </body>),
    então nenhum template existente precisa ser alterado.

Configuração da chave da IA (use UMA das opções):
  1) variável de ambiente GROQ_API_KEY (ou ANTHROPIC_API_KEY)
  2) arquivo assistente/config.env com a linha: GROQ_API_KEY=sua_chave

Sem chave, o assistente continua funcionando em "modo básico" (ajuda de navegação),
sem dar erro.
"""
import json
import os
import time
import urllib.error
import urllib.request

from flask import Blueprint, jsonify, request

PASTA = os.path.dirname(os.path.abspath(__file__))

bp = Blueprint(
    "assistente",
    __name__,
    url_prefix="/assistente",
    static_folder=os.path.join(PASTA, "static"),
    static_url_path="/static",
)

TAG_WIDGET = '<script src="/assistente/static/assistente.js" defer></script>'

PAGINAS = {
    "/": "Início (entrada/saída de itens do estoque)",
    "/index": "Início (entrada/saída de itens do estoque)",
    "/login": "Login do administrador",
    "/loginusuario": "Login do usuário",
    "/estoque": "Estoque (lista de itens do almoxarifado)",
    "/historico": "Histórico de movimentações",
    "/criacaoitem": "Criação de item",
    "/solicitar": "Solicitação de itens",
    "/tabela": "Tabela de itens",
    "/criacaouser": "Criação de usuário",
}

SYSTEM_PROMPT = """Você é a Assis, a assistente virtual do sistema de Almoxarifado.
Responda sempre em português do Brasil, de forma curta, clara e amigável.

O sistema tem estas páginas:
- Início (/index): registrar entrada de itens no estoque.
- Criação de item (/criacaoItem): cadastrar um novo item (nome, quantidade, estoque mínimo, descrição, preço, categoria, imagem).
- Estoque (/estoque): consultar os itens do almoxarifado.
- Tabela (/tabela): ver os itens em formato de tabela.
- Solicitar (/solicitar): solicitar retirada de itens.
- Histórico (/historico): ver as movimentações (nome, quantidade e ação).
- Criação de usuário (/criacaoUser): cadastrar funcionários.
- Login (/login) e Login de usuário (/loginusuario).

Regras:
- Ajude o usuário a usar o sistema, explicando em qual página fazer cada tarefa.
- Se receber dados do estoque no contexto, use-os para responder; nunca invente itens ou quantidades.
- Se não souber algo, diga que não sabe e sugira falar com o responsável pelo almoxarifado.
- Nunca peça nem mostre senhas.
- Não responda sobre assuntos sem relação com o almoxarifado; redirecione com educação."""


# ----------------------------------------------------------------- configuração
def _carregar_config_env():
    caminho = os.path.join(PASTA, "config.env")
    valores = {}
    if os.path.isfile(caminho):
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    k, v = linha.split("=", 1)
                    valores[k.strip()] = v.strip().strip('"').strip("'")
    return valores


def _cfg(nome, padrao=""):
    return os.environ.get(nome) or _carregar_config_env().get(nome) or padrao


def _chave_e_provedor():
    """Groq tem prioridade; se não houver, tenta Anthropic."""
    g = _cfg("GROQ_API_KEY")
    if g:
        return g, "groq"
    a = _cfg("ANTHROPIC_API_KEY")
    if a:
        return a, "anthropic"
    return "", ""


# ----------------------------------------------------------------- contexto do estoque (opcional)
_cache_estoque = {"t": 0, "texto": ""}


def _resumo_estoque():
    """Tenta ler um resumo do estoque no MySQL. Se falhar, segue sem contexto."""
    if _cfg("ASSISTENTE_USAR_BANCO", "1") != "1":
        return ""
    if time.time() - _cache_estoque["t"] < 60:
        return _cache_estoque["texto"]

    texto = ""
    try:
        import mysql.connector  # já está no requirements.txt

        conn = mysql.connector.connect(
            host=_cfg("DB_HOST", "db_almox"),
            user=_cfg("DB_USER", "root"),
            password=_cfg("DB_PASSWORD", "root"),
            database=_cfg("DB_NAME", "TCC"),
            connection_timeout=2,
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT nome, quantidade, estoque_minimo, categoria "
            "FROM estoque_almoxarifado ORDER BY nome LIMIT 200"
        )
        linhas = cur.fetchall()
        cur.close()
        conn.close()

        itens, baixos = [], []
        for nome, qtd, minimo, cat in linhas:
            itens.append(f"{nome} (qtd: {qtd}, mínimo: {minimo}, categoria: {cat})")
            try:
                if float(qtd) <= float(minimo):
                    baixos.append(nome)
            except (TypeError, ValueError):
                pass
        if itens:
            texto = "Itens no estoque: " + "; ".join(itens) + "."
            if baixos:
                texto += " Itens com estoque baixo (quantidade <= mínimo): " + ", ".join(baixos) + "."
    except Exception:
        texto = ""

    _cache_estoque.update(t=time.time(), texto=texto)
    return texto


# ----------------------------------------------------------------- resposta básica (sem chave)
def _resposta_basica(pergunta):
    p = pergunta.lower()
    regras = [
        (("criar item", "novo item", "cadastrar item", "criação de item", "criacao de item"),
         "Para cadastrar um item novo, abra a página **Criação de item** (/criacaoItem)."),
        (("entrada", "dar entrada", "adicionar estoque", "repor"),
         "Para registrar a entrada de itens, use a página **Início** (/index)."),
        (("solicit", "retirar", "pedir"),
         "Para solicitar itens, use a página **Solicitar** (/solicitar)."),
        (("histór", "histor", "movimenta"),
         "As movimentações ficam na página **Histórico** (/historico)."),
        (("estoque", "tabela", "consultar", "quantidade"),
         "Você pode consultar os itens em **Estoque** (/estoque) ou em **Tabela** (/tabela)."),
        (("usuário", "usuario", "funcionário", "funcionario", "cadastrar user"),
         "Para cadastrar um usuário, use a página **Criação de usuário** (/criacaoUser)."),
        (("login", "entrar", "acessar"),
         "O acesso é feito em **Login** (/login) ou **Login de usuário** (/loginusuario)."),
    ]
    for chaves, resp in regras:
        if any(c in p for c in chaves):
            return resp
    return ("Posso te ajudar a encontrar a página certa: criação de item, entrada, solicitação, "
            "estoque, tabela, histórico ou criação de usuário. Sobre o que você precisa?")


# ----------------------------------------------------------------- chamada à IA
def _chamar_ia(mensagens, pagina_desc, chave, provedor):
    sistema = SYSTEM_PROMPT
    if pagina_desc:
        sistema += f"\n\nO usuário está agora na página: {pagina_desc}."
    estoque = _resumo_estoque()
    if estoque:
        sistema += f"\n\nDados atuais do estoque (somente leitura): {estoque}"

    if provedor == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        corpo = {
            "model": _cfg("ASSISTENTE_MODEL", "llama-3.3-70b-versatile"),
            "max_tokens": 700,
            "temperature": 0.3,
            "messages": [{"role": "system", "content": sistema}] + mensagens,
        }
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer " + chave,
            "user-agent": "almoxarifado-assis/1.0",  # evita bloqueio do Cloudflare
        }
    else:
        url = "https://api.anthropic.com/v1/messages"
        corpo = {
            "model": _cfg("ASSISTENTE_MODEL", "claude-sonnet-5-5"),
            "max_tokens": 700,
            "system": sistema,
            "messages": mensagens,
        }
        headers = {
            "content-type": "application/json",
            "x-api-key": chave,
            "anthropic-version": "2023-06-01",
        }

    req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=40) as r:
        dados = json.loads(r.read().decode("utf-8"))

    if provedor == "groq":
        return (dados["choices"][0]["message"].get("content") or "").strip()
    return "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text").strip()


def _limpar_historico(bruto):
    """Mantém só mensagens válidas, últimas 12, começando por 'user' e alternando papéis."""
    limpas = []
    for m in (bruto or [])[-12:]:
        if not isinstance(m, dict):
            continue
        papel, texto = m.get("role"), str(m.get("content", "")).strip()[:2000]
        if papel in ("user", "assistant") and texto:
            if limpas and limpas[-1]["role"] == papel:
                limpas[-1]["content"] += "\n" + texto
            else:
                limpas.append({"role": papel, "content": texto})
    while limpas and limpas[0]["role"] != "user":
        limpas.pop(0)
    return limpas


# ----------------------------------------------------------------- rotas
@bp.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json(silent=True) or {}
    mensagens = _limpar_historico(dados.get("messages"))
    if not mensagens or mensagens[-1]["role"] != "user":
        return jsonify(reply="Digite sua pergunta para eu poder ajudar."), 400

    caminho = str(dados.get("page", "/")).lower().rstrip("/").replace(".html", "") or "/"
    pagina_desc = PAGINAS.get(caminho, "")

    chave, provedor = _chave_e_provedor()
    if not chave:
        return jsonify(reply=_resposta_basica(mensagens[-1]["content"]), mode="basic")

    try:
        resposta = _chamar_ia(mensagens, pagina_desc, chave, provedor)
        return jsonify(reply=resposta or "Não consegui gerar uma resposta. Tente reformular.", mode="ai")
    except urllib.error.HTTPError as e:
        motivo = "chave de API inválida" if e.code in (401, 403) else f"erro {e.code} no serviço de IA"
        return jsonify(reply=f"Não consegui falar com a IA agora ({motivo}).\n\n" + _resposta_basica(mensagens[-1]["content"]), mode="basic")
    except Exception:
        return jsonify(reply="Não consegui falar com a IA agora. Tente de novo em instantes.\n\n" + _resposta_basica(mensagens[-1]["content"]), mode="basic")


@bp.route("/ping")
def ping():
    return jsonify(ok=True, ia=bool(_chave_e_provedor()[0]), provedor=_chave_e_provedor()[1])


# ----------------------------------------------------------------- injeção em todas as páginas
def _injetar_widget(resp):
    try:
        if (
            resp.status_code == 200
            and not resp.direct_passthrough
            and resp.mimetype == "text/html"
            and not request.path.startswith("/assistente")
        ):
            html = resp.get_data(as_text=True)
            if "assistente.js" not in html:
                idx = html.lower().rfind("</body>")
                html = html[:idx] + TAG_WIDGET + html[idx:] if idx != -1 else html + TAG_WIDGET
                resp.set_data(html)
    except Exception:
        pass  # nunca quebra a página por causa do assistente
    return resp


def init_assistente(app):
    app.register_blueprint(bp)
    app.after_request(_injetar_widget)
