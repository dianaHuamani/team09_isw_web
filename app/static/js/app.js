const menuButton = document.getElementById('menuToggle');
const navigation = document.getElementById('mainNav');
menuButton?.addEventListener('click', () => navigation?.classList.toggle('open'));
document.querySelectorAll('.flash-close').forEach((button) => {
  button.addEventListener('click', () => button.closest('.flash')?.remove());
});
