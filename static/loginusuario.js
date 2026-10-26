function verificar2() {
    const usuario = document.getElementById("user").value;
    const senha = document.getElementById("senha").value;

    const usuarioCorreto = "User";
    const senhaCorreta = "2000";

    if (usuario === usuarioCorreto && senha === senhaCorreta) {
        
        window.location.href = "/templates/estoque.html"

    }else{

        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'usuario ou senha incorretos',
            confirmButtonColor: '#3c61a5'

        });
    }
    }