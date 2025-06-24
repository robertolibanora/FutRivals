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
  if(menuToggle && navLinks && navOverlay) {
    menuToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      navLinks.classList.toggle('open');
      navOverlay.classList.toggle('open');
      if(navLinks.classList.contains('open')) {
        navLinks.style.display = 'flex';
        navLinks.focus && navLinks.focus();
      } else {
        navLinks.style.display = '';
      }
    });
    // Chiudi il menu quando clicchi su un link (mobile UX)
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navOverlay.classList.remove('open');
        navLinks.style.display = '';
      });
    });
    // Chiudi il menu se clicchi sull'overlay
    navOverlay.addEventListener('click', function() {
      navLinks.classList.remove('open');
      navOverlay.classList.remove('open');
      navLinks.style.display = '';
    });
  }
});