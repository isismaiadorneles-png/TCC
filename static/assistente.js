// Estoque de exemplo (pode trocar pelos seus itens)
const estoque = {
  luva:      { nome: "Luvas",      qtd: 48,   local: "Corredor A, prateleira 2" },
  parafuso:  { nome: "Parafusos",  qtd: 1200, local: "Corredor B, gaveta 5" },
  capacete:  { nome: "Capacetes",  qtd: 6,    local: "Corredor A, prateleira 4" },
  fita:      { nome: "Fitas",      qtd: 30,   local: "Corredor C, prateleira 1" },
  caixa:     { nome: "Caixas",     qtd: 85,   local: "Galpão 2" }
};

const bolinha   = document.getElementById("bolinha");
const chat      = document.getElementById("chat");
const mensagens = document.getElementById("mensagens");
const texto     = document.getElementById("texto");

// Abrir e fechar
bolinha.onclick = () => {
  chat.style.display = "flex";
  bolinha.style.display = "none";
  if (mensagens.children.length === 0) {
    adicionar("Olá! Sou a assistente do almoxarifado. Digite “ajuda” para ver o que eu faço.", "bot");
  }
};

document.getElementById("fechar").onclick = () => {
  chat.style.display = "none";
  bolinha.style.display = "block";
};

// Enviar mensagem
document.getElementById("enviar").onclick = enviar;
texto.addEventListener("keydown", e => { if (e.key === "Enter") enviar(); });

function enviar() {
  const msg = texto.value.trim();
  if (msg === "") return;
  adicionar(msg, "usuario");
  texto.value = "";
  adicionar(responder(msg), "bot");
}

function adicionar(conteudo, tipo) {
  const div = document.createElement("div");
  div.className = "msg " + tipo;
  div.textContent = conteudo;
  mensagens.appendChild(div);
  mensagens.scrollTop = mensagens.scrollHeight;
}

// Lógica da assistente
function responder(msg) {
  // minúsculas e sem acentos
  const t = msg.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  // procura o item citado
  let item = null;
  for (const chave in estoque) {
    if (t.includes(chave)) item = estoque[chave];
  }

  // procura um número na frase
  const achou = t.match(/\d+/);
  const numero = achou ? parseInt(achou[0]) : 0;

  if (t.includes("ajuda")) {
    return "Pergunte, por exemplo:\n• quantas luvas tem?\n• onde fica o parafuso?\n• saida de 10 caixas\n• entrada de 20 fitas\n• listar estoque";
  }

  if (t.includes("listar") || t.includes("lista")) {
    let resposta = "Estoque atual:";
    for (const chave in estoque) {
      resposta += "\n• " + estoque[chave].nome + ": " + estoque[chave].qtd;
    }
    return resposta;
  }

  if (!item) {
    return "Não entendi. Digite “ajuda” para ver o que eu sei fazer.";
  }

  if (t.includes("onde") || t.includes("fica")) {
    return item.nome + " ficam em: " + item.local;
  }

  if (t.includes("saida") || t.includes("retirar")) {
    if (numero === 0) return "Quantas unidades saíram?";
    if (numero > item.qtd) return "Só temos " + item.qtd + " de " + item.nome.toLowerCase() + ".";
    item.qtd -= numero;
    return "Saída registrada. Agora temos " + item.qtd + " de " + item.nome.toLowerCase() + ".";
  }

  if (t.includes("entrada") || t.includes("chegou")) {
    if (numero === 0) return "Quantas unidades chegaram?";
    item.qtd += numero;
    return "Entrada registrada. Agora temos " + item.qtd + " de " + item.nome.toLowerCase() + ".";
  }

  // se só citou o item, mostra a quantidade
  return "Temos " + item.qtd + " de " + item.nome.toLowerCase() + ".";
}