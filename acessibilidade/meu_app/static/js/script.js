// Seleciona o formulário e o modal
const form = document.getElementById("analisarForm");
const loadingModal = document.getElementById("loadingModal");

// Adiciona um ouvinte de evento para o envio do formulário
form.addEventListener("submit", function (event) {
  // Exibe o modal de carregamento
  loadingModal.style.display = "flex";
});
