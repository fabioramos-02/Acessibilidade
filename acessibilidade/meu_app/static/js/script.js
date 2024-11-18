const form = document.getElementById("analisarForm");
const loadingModal = new bootstrap.Modal(
  document.getElementById("loadingModal")
);

form.addEventListener("submit", function (event) {
  loadingModal.show();
});
