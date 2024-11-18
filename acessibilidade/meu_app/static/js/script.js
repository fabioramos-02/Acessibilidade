document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analisarForm");
  const loadingModal = new bootstrap.Modal(
    document.getElementById("loadingModal")
  );

  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Previna comportamento padrão para testes
    loadingModal.show();
    // Remova o preventDefault em produção para que o formulário seja enviado
    form.submit();
  });
});
