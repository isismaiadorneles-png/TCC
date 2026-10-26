async function senha() {
    const { value: password } = await Swal.fire({
  title: "Acesso restrito",
  input: "password",
  inputLabel: "Digite a senha padrao para proseguir!",
  inputPlaceholder: "Senha",
  inputAttributes: {
    maxlength: "10",
    autocapitalize: "off",
    autocorrect: "off"
  }
});
if (password === '1234') { 
        // Se a senha estiver correta, redireciona para a rota do Flask
        window.location.href = "/login.html"; 
    } else if (password) {
        // Se digitou algo errado
        Swal.fire({
            icon: "error",
            title: "Acesso Negado",
            text: "Senha incorreta!"
        });
    }
}