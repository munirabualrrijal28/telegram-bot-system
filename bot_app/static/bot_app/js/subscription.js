// Subscription Page JavaScript - Activation functionality

window.activateSubscription = function(activationUrl, csrfToken) {
  if (this.activating || !this.activationCode) return;

  this.activating = true;
  const code = this.activationCode.trim();

  fetch(activationUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ code: code }),
  })
    .then((res) => res.json())
    .then((data) => {
      this.activating = false;
      if (data.success) {
        showToast(
          data.message || "Subscription activated successfully!",
          "success"
        );
        this.activationModalOpen = false;
        this.activationCode = "";
        // Reload page to show updated subscription
        setTimeout(() => window.location.reload(), 1500);
      } else {
        showToast(data.error || "Failed to activate subscription", "error");
      }
    })
    .catch((err) => {
      this.activating = false;
      console.error(err);
      showToast("An error occurred. Please try again.", "error");
    });
};
