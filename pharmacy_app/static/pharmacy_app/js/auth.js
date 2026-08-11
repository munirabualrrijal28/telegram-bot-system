// Auth page JavaScript - Form toggling

// Toggle between login and signup forms
function toggleForm(event) {
  event.preventDefault();
  const container = document.getElementById('authContainer');
  if (container) {
    container.classList.toggle('show-signup');
  }
}

// Make function globally accessible
window.toggleForm = toggleForm;
