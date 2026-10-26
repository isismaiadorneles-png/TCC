const botoes = document.querySelectorAll(".btn-setor");
botoes.forEach(botao => {
  botao.addEventListener("click", () => {
    botoes.forEach(btn => {
      btn.classList.remove("ativo");
    });
    botao.classList.add("ativo");  
  });
});

function alerta(){
  Swal.fire({
  title: "Solicitação enviada",
  icon: "success",
  draggable: true
});
}