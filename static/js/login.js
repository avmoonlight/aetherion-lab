function togglePassword() {
    const senhaInput = document.getElementById('senha');
    const icon = document.querySelector('.toggle-password');

    if (senhaInput.type === 'password') {
        senhaInput.type = 'text';
        icon.textContent = '🙈'; // ícone para esconder
    } else {
        senhaInput.type = 'password';
        icon.textContent = '👁️'; // ícone para mostrar
    }
}
