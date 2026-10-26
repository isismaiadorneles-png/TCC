(function () {
  if (window.__assisAlmox) return;
  window.__assisAlmox = true;

  var KEY = "assis_almox_v1";
  var estado = { aberto: false, msgs: [] };
  try {
    var salvo = JSON.parse(sessionStorage.getItem(KEY) || "null");
    if (salvo) estado = salvo;
  } catch (e) {}

  function salvar() {
    try { sessionStorage.setItem(KEY, JSON.stringify(estado)); } catch (e) {}
  }

  var CSS = `
    :host { all: initial; }
    * { box-sizing: border-box; font-family: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif; }
    .fab {
      position: fixed; right: 22px; bottom: 22px; z-index: 2147483000;
      width: 58px; height: 58px; border-radius: 50%; border: 0; cursor: pointer;
      background: #F86803; color: #fff; display: grid; place-items: center;
      box-shadow: 0 6px 18px rgba(14,48,150,.35);
      transition: transform .15s ease, background .15s ease;
    }
    .fab:hover { background: #AF3A00; transform: scale(1.06); }
    .fab:focus-visible, button:focus-visible, textarea:focus-visible { outline: 3px solid #0282B5; outline-offset: 2px; }
    .fab svg { width: 28px; height: 28px; }
    .painel {
      position: fixed; right: 22px; bottom: 94px; z-index: 2147483000;
      width: 370px; max-width: calc(100vw - 24px); height: 520px; max-height: calc(100vh - 118px);
      display: none; flex-direction: column; overflow: hidden;
      background: #fff; border-radius: 14px; border: 1px solid #b5c5d5;
      box-shadow: 0 16px 40px rgba(29,50,115,.28);
    }
    .painel.aberto { display: flex; animation: abre .18s ease-out; }
    @keyframes abre { from { opacity: 0; transform: translateY(10px) scale(.98); } to { opacity: 1; transform: none; } }
    @media (prefers-reduced-motion: reduce) { .painel.aberto { animation: none; } .fab { transition: none; } }
    header { background: #0E3096; color: #fff; padding: 12px 14px; display: flex; align-items: center; gap: 10px; }
    header .avatar { width: 34px; height: 34px; border-radius: 50%; background: #F86803; display: grid; place-items: center; flex: none; }
    header .avatar svg { width: 20px; height: 20px; }
    header .titulo { flex: 1; min-width: 0; }
    header strong { display: block; font-size: 15px; line-height: 1.2; }
    header span { font-size: 12px; opacity: .85; }
    header button { background: transparent; border: 0; color: #fff; cursor: pointer; padding: 6px; border-radius: 6px; font-size: 18px; line-height: 1; }
    header button:hover { background: rgba(255,255,255,.15); }
    .msgs { flex: 1; overflow-y: auto; padding: 14px; background: #eaedef; display: flex; flex-direction: column; gap: 10px; }
    .m { max-width: 86%; padding: 9px 12px; border-radius: 12px; font-size: 14px; line-height: 1.45; word-wrap: break-word; overflow-wrap: anywhere; }
    .m.bot { background: #fff; color: #1D3273; border: 1px solid #b5c5d5; border-bottom-left-radius: 4px; align-self: flex-start; }
    .m.user { background: #0E3096; color: #fff; border-bottom-right-radius: 4px; align-self: flex-end; }
    .m ul { margin: 6px 0 2px 18px; padding: 0; }
    .m p { margin: 0 0 6px; } .m p:last-child { margin-bottom: 0; }
    .m code { background: rgba(0,0,0,.08); padding: 1px 4px; border-radius: 4px; font-size: 13px; }
    .digitando { display: inline-flex; gap: 4px; padding: 12px; }
    .digitando i { width: 7px; height: 7px; border-radius: 50%; background: #b5c5d5; animation: pulsa 1s infinite; }
    .digitando i:nth-child(2) { animation-delay: .15s; } .digitando i:nth-child(3) { animation-delay: .3s; }
    @keyframes pulsa { 0%,60%,100% { opacity: .35; } 30% { opacity: 1; } }
    .sugestoes { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 14px 10px; background: #eaedef; }
    .sugestoes button { background: #fff; border: 1px solid #0282B5; color: #0E3096; border-radius: 999px; padding: 5px 10px; font-size: 12.5px; cursor: pointer; }
    .sugestoes button:hover { background: #AAD5F9; }
    form { display: flex; gap: 8px; padding: 10px; background: #fff; border-top: 1px solid #b5c5d5; align-items: flex-end; }
    textarea { flex: 1; resize: none; border: 1px solid #b5c5d5; border-radius: 10px; padding: 9px 10px; font-size: 14px; max-height: 90px; min-height: 38px; color: #1D3273; }
    form button { border: 0; background: #F86803; color: #fff; border-radius: 10px; width: 42px; height: 38px; cursor: pointer; display: grid; place-items: center; flex: none; }
    form button:hover { background: #AF3A00; }
    form button:disabled { background: #b5c5d5; cursor: not-allowed; }
    form button svg { width: 18px; height: 18px; }
    @media (max-width: 480px) {
      .painel { right: 12px; bottom: 84px; height: calc(100vh - 104px); }
      .fab { right: 14px; bottom: 14px; }
    }
  `;

  var ICON_CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><circle cx="9" cy="12" r=".6" fill="currentColor"/><circle cx="13" cy="12" r=".6" fill="currentColor"/><circle cx="17" cy="12" r=".6" fill="currentColor"/></svg>';
  var ICON_SEND = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.4 20.4 21 12 3.4 3.6 3.3 10l12.6 2-12.6 2z"/></svg>';

  var host = document.createElement("div");
  host.id = "assis-almox-host";
  document.body.appendChild(host);
  var root = host.attachShadow({ mode: "open" });

  root.innerHTML =
    "<style>" + CSS + "</style>" +
    '<button class="fab" type="button" aria-label="Abrir assistente virtual" aria-expanded="false">' + ICON_CHAT + "</button>" +
    '<section class="painel" role="dialog" aria-label="Assistente virtual do almoxarifado">' +
      '<header><div class="avatar">' + ICON_CHAT + '</div>' +
      '<div class="titulo"><strong>Assis</strong><span>Assistente do almoxarifado</span></div>' +
      '<button type="button" data-acao="limpar" title="Nova conversa" aria-label="Nova conversa">&#8635;</button>' +
      '<button type="button" data-acao="fechar" title="Fechar" aria-label="Fechar assistente">&#10005;</button></header>' +
      '<div class="msgs" aria-live="polite"></div>' +
      '<div class="sugestoes"></div>' +
      '<form><textarea rows="1" placeholder="Digite sua dúvida..." aria-label="Mensagem"></textarea>' +
      '<button type="submit" aria-label="Enviar">' + ICON_SEND + "</button></form>" +
    "</section>";

  var fab = root.querySelector(".fab");
  var painel = root.querySelector(".painel");
  var msgsEl = root.querySelector(".msgs");
  var sugEl = root.querySelector(".sugestoes");
  var form = root.querySelector("form");
  var campo = root.querySelector("textarea");
  var enviar = root.querySelector('form button');
  var ocupado = false;

  var SUGESTOES = ["Como criar um item?", "Como dar entrada no estoque?", "Quais itens estão com estoque baixo?", "Onde vejo o histórico?"];
  var SAUDACAO = "Olá! Eu sou a Assis, a assistente do almoxarifado. Posso ajudar a cadastrar itens, dar entrada, solicitar materiais e consultar o estoque. Como posso ajudar?";

  function esc(t) {
    return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function formatar(t) {
    var linhas = esc(t).split(/\n/), out = [], lista = false;
    linhas.forEach(function (l) {
      var li = l.match(/^\s*[-*•]\s+(.*)$/);
      l = l.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`(.+?)`/g, "<code>$1</code>");
      if (li) {
        if (!lista) { out.push("<ul>"); lista = true; }
        out.push("<li>" + li[1].replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</li>");
      } else {
        if (lista) { out.push("</ul>"); lista = false; }
        if (l.trim()) out.push("<p>" + l + "</p>");
      }
    });
    if (lista) out.push("</ul>");
    return out.join("");
  }

  function addMsg(papel, texto, persistir) {
    var d = document.createElement("div");
    d.className = "m " + (papel === "user" ? "user" : "bot");
    d.innerHTML = papel === "user" ? esc(texto) : formatar(texto);
    msgsEl.appendChild(d);
    msgsEl.scrollTop = msgsEl.scrollHeight;
    if (persistir !== false) {
      estado.msgs.push({ role: papel === "user" ? "user" : "assistant", content: texto });
      salvar();
    }
    return d;
  }

  function desenhar() {
    msgsEl.innerHTML = "";
    if (!estado.msgs.length) {
      addMsg("bot", SAUDACAO, false);
    } else {
      estado.msgs.forEach(function (m) { addMsg(m.role, m.content, false); });
    }
    sugEl.style.display = estado.msgs.length ? "none" : "flex";
  }

  function abrir(v) {
    estado.aberto = v;
    painel.classList.toggle("aberto", v);
    fab.setAttribute("aria-expanded", String(v));
    fab.setAttribute("aria-label", v ? "Fechar assistente virtual" : "Abrir assistente virtual");
    salvar();
    if (v) { msgsEl.scrollTop = msgsEl.scrollHeight; setTimeout(function () { campo.focus(); }, 50); }
  }

  function perguntar(texto) {
    texto = (texto || "").trim();
    if (!texto || ocupado) return;
    ocupado = true; enviar.disabled = true;
    sugEl.style.display = "none";
    addMsg("user", texto);
    campo.value = ""; campo.style.height = "auto";

    var dig = document.createElement("div");
    dig.className = "m bot digitando";
    dig.innerHTML = "<i></i><i></i><i></i>";
    msgsEl.appendChild(dig);
    msgsEl.scrollTop = msgsEl.scrollHeight;

    fetch("/assistente/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: estado.msgs, page: location.pathname })
    })
      .then(function (r) { return r.json(); })
      .then(function (d) { dig.remove(); addMsg("bot", d.reply || "Não consegui responder agora."); })
      .catch(function () { dig.remove(); addMsg("bot", "Não consegui me conectar ao servidor. Verifique sua conexão e tente novamente."); })
      .finally(function () { ocupado = false; enviar.disabled = false; campo.focus(); });
  }

  SUGESTOES.forEach(function (s) {
    var b = document.createElement("button");
    b.type = "button"; b.textContent = s;
    b.addEventListener("click", function () { perguntar(s); });
    sugEl.appendChild(b);
  });

  fab.addEventListener("click", function () { abrir(!estado.aberto); });
  root.querySelector('[data-acao="fechar"]').addEventListener("click", function () { abrir(false); fab.focus(); });
  root.querySelector('[data-acao="limpar"]').addEventListener("click", function () { estado.msgs = []; salvar(); desenhar(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); perguntar(campo.value); });
  campo.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); perguntar(campo.value); }
    if (e.key === "Escape") { abrir(false); fab.focus(); }
  });
  campo.addEventListener("input", function () {
    campo.style.height = "auto";
    campo.style.height = Math.min(campo.scrollHeight, 90) + "px";
  });

  desenhar();
  abrir(!!estado.aberto);
})();
