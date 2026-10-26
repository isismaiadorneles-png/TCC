function verificar() {
    const usuario = document.getElementById("user").value;
    const senha = document.getElementById("senha").value;

    const usuarioCorreto = "SouADM";
    const senhaCorreta = "1000";

    if (usuario === usuarioCorreto && senha === senhaCorreta) {
        
        window.location.href = "/estoque.html"

    }else{

        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'usuario ou senha incorretos',
            confirmButtonColor: '#3c61a5'

        });
    }
    }