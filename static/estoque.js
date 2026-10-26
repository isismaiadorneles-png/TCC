document.addEventListener('DOMContentLoaded', () => {
  const botao = document.getElementById('botaofiltro');
  const conteudo = document.getElementById('conteudo-container');

  // Garante que o botão e o conteúdo realmente existem na página
  if (botao && conteudo) {
    botao.addEventListener('click', (event) => {
     
      // Mostra/Esconde o conteúdo
      conteudo.classList.toggle('escondido');
    });
  } else {
    console.error("Não encontrei o botão ou o conteúdo! Verifique os IDs.");
  }
});

botao.addEventListener('click', () => {
  conteudo.classList.toggle('escondido');
});

function ampliarImagem(srcCaminho) {
    // Pega o modal e a tag da imagem grande
    var modal = document.getElementById("meuModal");
    var imgGrande = document.getElementById("imagemGrande");
    
    // Passa o caminho da imagem clicada para a imagem grande e mostra o modal
    imgGrande.src = srcCaminho;
    modal.style.display = "flex";
}

function fecharImagem() {
    // Esconde o modal novamente
    document.getElementById("meuModal").style.display = "none";
}