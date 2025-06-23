// Toggle mobile menu
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
  }

  // Aggiornamento automatico della pagina ogni 30 secondi
  setTimeout(() => {
    window.location.reload();
  }, 60000); // 30000 ms = 30 secondi
});