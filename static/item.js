const botao = document.getElementById('meuBotao');

// Quando o mouse entra no botão
botao.addEventListener('mouseover', function botaoentrar() {
    botao.style.backgroundColor = 'blue'; // Cor nova
    botao.style.color = 'white';
});

// Quando o mouse sai do botão (reverte a cor)
botao.addEventListener('mouseout', function() {
    const elemento = document.getElementById("botaoentrar");
    botao.style.backgroundColor = 'white'; // Volta ao padrão do CSS
    botao.style.color = 'white';
});

function botaoentrar() {
    document.getElementById("botaoentrar").style.backgroundColor = "lightblue";
}
function botaovoltar() {
    document.getElementById("botaovoltar").style.backgroundColor = "blue";
}