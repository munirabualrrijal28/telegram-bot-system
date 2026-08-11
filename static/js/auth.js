function toggleForm(event) {
  event.preventDefault();
  const container = document.getElementById("authContainer");
  container.classList.toggle("show-signup");
}
