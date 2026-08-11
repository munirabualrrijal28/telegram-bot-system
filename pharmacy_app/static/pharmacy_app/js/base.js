// Tailwind CSS Configuration
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        sidebar: {
          dark: "#1a2332",
          darker: "#0f1419",
        },
      },
    },
  },
};

// Global toast notification function
function showToast(message, type = "success") {
  const container = document.getElementById("globalToastContainer");
  if (!container) return;

  // Map Django message tags to types
  const typeMap = {
    success: "success",
    error: "error",
    danger: "error",
    warning: "warning",
    info: "info",
    update: "update",
  };

  let toastType = typeMap[type];

  // Handle composite tags or missing types
  if (!toastType) {
    if (type.includes("update")) toastType = "update";
    else if (type.includes("error")) toastType = "error";
    else if (type.includes("warning")) toastType = "warning";
    else if (type.includes("info")) toastType = "info";
    else toastType = "success";
  }

  // Color and icon mappings
  const styles = {
    success: { bg: "bg-green-500", icon: "fa-check-circle" },
    error: { bg: "bg-red-500", icon: "fa-exclamation-circle" },
    warning: { bg: "bg-yellow-500", icon: "fa-exclamation-triangle" },
    info: { bg: "bg-blue-500", icon: "fa-info-circle" },
    update: { bg: "bg-blue-500", icon: "fa-check-circle" },
  };

  const style = styles[toastType] || styles.success;

  const toast = document.createElement("div");
  toast.className = `${style.bg} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 transform transition-all duration-300 ease-in-out opacity-0 translate-x-full`;
  toast.innerHTML = `
    <i class="fas ${style.icon} text-lg"></i>
    <span class="flex-1 text-sm font-medium">${message}</span>
    <button onclick="this.parentElement.remove()" class="hover:bg-white hover:bg-opacity-20 rounded p-1 transition-colors">
      <i class="fas fa-times text-sm"></i>
    </button>
  `;

  container.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.classList.remove("opacity-0", "translate-x-full");
  }, 10);

  // Auto-dismiss
  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-x-full");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Make it globally accessible
window.showToast = showToast;

// Check for session storage toast on load
document.addEventListener("DOMContentLoaded", function () {
  const storedToast = sessionStorage.getItem("toastMessage");
  if (storedToast) {
    try {
      const { message, type } = JSON.parse(storedToast);
      showToast(message, type);
    } catch (e) {
      console.error("Error parsing stored toast", e);
    }
    sessionStorage.removeItem("toastMessage");
  }
});
