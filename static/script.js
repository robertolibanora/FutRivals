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

document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');
  const navOverlay = document.getElementById('nav-overlay');

  // Mobile hamburger menu
  if(menuToggle && navLinks && navOverlay) {
    menuToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      const isOpen = navLinks.classList.toggle('open');
      navOverlay.classList.toggle('open', isOpen);
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navOverlay.classList.remove('open');
      });
    });
    navOverlay.addEventListener('click', function() {
      navLinks.classList.remove('open');
      navOverlay.classList.remove('open');
    });
  }

  // Aggiornamento automatico della pagina ogni 60 secondi
  setTimeout(() => {
    window.location.reload();
  }, 60000);
});