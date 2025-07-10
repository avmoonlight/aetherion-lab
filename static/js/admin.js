// Abrir popups
function abrirPopup(id) {
  document.getElementById(id).style.display = "flex";
}

// Fechar popups
function fecharPopup(id) {
  document.getElementById(id).style.display = "none";
}

// Voltar ao topo suavemente (caso queira garantir compatibilidade extra)
document.addEventListener("DOMContentLoaded", function () {
  const btnTopo = document.getElementById("btn-topo");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      btnTopo.style.display = "block";
    } else {
      btnTopo.style.display = "none";
    }
  });

  btnTopo.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });


  const ctxBarra = document.getElementById('graficoBarra');
  const ctxPizza = document.getElementById('graficoPizza');

  new Chart(ctxBarra, {
    type: 'bar',
    data: {
      labels: ['Usuário A', 'Usuário B', 'Usuário C'],
      datasets: [{
        label: 'Número de Acessos',
        data: [12, 19, 7],
        backgroundColor: '#a855f7'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          ticks: { color: '#fff' },
          grid: { color: 'rgba(255,255,255,0.1)' }
        },
        x: {
          ticks: { color: '#fff' },
          grid: { color: 'rgba(255,255,255,0.1)' }
        }
      }
    }
  });

  new Chart(ctxPizza, {
    type: 'pie',
    data: {
      labels: ['Ativo', 'Inativo'],
      datasets: [{
        label: 'Status dos Usuários',
        data: [80, 20],
        backgroundColor: ['#a855f7', '#9333ea']
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: '#fff' } }
      }
    }
  });})

  // Abre modal de edição com dados do usuário
function abrirModalEditar(usuario) {
  document.getElementById("modalEditar").style.display = "block";
  document.getElementById("editUserId").value = usuario.id;
  document.getElementById("editNome").value = usuario.nome;
  document.getElementById("editLogin").value = usuario.login;
  document.getElementById("editSenha").value = usuario.senha;
  document.getElementById("editFoto").value = usuario.foto;
}

// Modal de exclusão
function abrirModalExcluir(userId) {
  document.getElementById("modalExcluir").style.display = "block";
  document.getElementById("deleteUserId").value = userId;
}

// Fechar modal
function fecharModal(id) {
  document.getElementById(id).style.display = "none";
}

// Confirmar exclusão (exemplo com fetch)
function confirmarExclusao() {
  const userId = document.getElementById("deleteUserId").value;
  
  fetch(`/api/usuarios/${userId}`, {
    method: 'DELETE'
  }).then(res => {
    if (res.ok) {
      alert("Usuário excluído com sucesso!");
      fecharModal('modalExcluir');
      location.reload();
    }
  });
}


