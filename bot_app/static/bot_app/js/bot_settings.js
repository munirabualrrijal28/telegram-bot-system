// Bot Settings Page JavaScript - Alpine.js Component
// NOTE: Django URLs are passed via data attributes in HTML

window.botSettings = function(urls) {
  return {
    isModalOpen: false,
    modalTitle: "",
    currentBotId: null,
    showToken: false,
    tokenReadonly: false,
    enableEditing: false,
    showDeleteConfirm: false,
    botToDelete: null,
    formData: {
      workspace_name: "",
      language: "en",
      telegram_token: "",
      bot_username: "",
      is_active: false,
      welcome_message: "👋 Welcome to our bot! How can we help you?",
      fallback_message: "❗Sorry, I couldn't find an answer to that.",
      start_keywords: "hi,hello,hey,start,Hi,Hello,Hey,Start,مرحبا,السلام عليكم,أهلا,اهلا,أهلا وسهلا",
      working_hours_start: "09:00",
      working_hours_end: "18:00",
    },

    newKeyword: "",
    keywords: [],

    init() {
        // Watch for changes in formData.start_keywords to keep keywords in sync
        this.$watch('formData.start_keywords', (value) => {
            this.initKeywords();
        });
    },

    initKeywords() {
        const value = this.formData.start_keywords;
        if (value) {
            this.keywords = value.split(',').map(k => k.trim()).filter(k => k);
        } else {
            this.keywords = [];
        }
    },

    addKeyword() {
        const trimmed = this.newKeyword.trim();
        if (trimmed && !this.keywords.includes(trimmed)) {
            this.keywords.push(trimmed);
            this.updateKeywordsString();
        }
        this.newKeyword = '';
    },

    removeKeyword(index) {
        this.keywords.splice(index, 1);
        this.updateKeywordsString();
    },

    updateKeywordsString() {
        this.formData.start_keywords = this.keywords.join(',');
    },

    restoreDefaults() {
        this.formData.start_keywords = "hi,hello,hey,start,Hi,Hello,Hey,Start,مرحبا,السلام عليكم,أهلا,اهلا,أهلا وسهلا";
        this.initKeywords();
    },

    getCsrfToken() {
      return (
        document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
        urls.csrfToken
      );
    },

    openAddModal() {
      this.modalTitle = "Add New Bot";
      this.currentBotId = null;
      this.tokenReadonly = false;
      this.enableEditing = false;
      this.showToken = false;
      this.resetForm();
      this.isModalOpen = true;
      this.initKeywords(); // Ensure keywords are initialized
    },

    openEditModal(botId) {
      this.modalTitle = "Bot Details";
      this.currentBotId = botId;
      this.tokenReadonly = true;
      this.enableEditing = false;
      this.showToken = false;
      this.isModalOpen = true;

      fetch(
        urls.botDetailsUrl.replace(
          "00000000-0000-0000-0000-000000000000",
          botId
        )
      )
        .then((res) => res.json())
        .then((response) => {
          if (response.success) {
            // Backend returns data in 'data' key
            this.formData = { ...response.data };
            this.initKeywords(); // Initialize keywords from fetched data
            this.modalTitle = `Bot Details - @${
              response.data.bot_username || "Not connected"
            }`;
          } else {
            showToast(
              response.error || "Failed to load bot details",
              "error"
            );
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error loading bot details", "error");
        });
    },

    closeModal() {
      this.isModalOpen = false;
      setTimeout(() => this.resetForm(), 200);
    },

    resetForm() {
      this.formData = {
        workspace_name: "",
        language: "en",
        telegram_token: "",
        bot_username: "",
        is_active: false,
        welcome_message:
          "👋 Welcome to our bot! How can we help you?",
        fallback_message: "❗Sorry, I couldn't find an answer to that.",
        start_keywords: "hi,hello,hey,start,Hi,Hello,Hey,Start,مرحبا,السلام عليكم,أهلا,اهلا,أهلا وسهلا",
        working_hours_start: "09:00",
        working_hours_end: "18:00",
      };
      this.showToken = false;
      this.tokenReadonly = false;
      this.enableEditing = false;
      this.initKeywords(); // Reset keywords
    },

    saveBot() {
      const formData = new FormData();
      formData.append("action", "save");
      if (this.currentBotId) {
        formData.append("bot_id", this.currentBotId);
      }
      Object.keys(this.formData).forEach((key) => {
        let value = this.formData[key];
        // Handle null/undefined values to avoid sending "null" string
        if (value === null || value === undefined) {
          value = "";
        }
        formData.append(key, value);
      });
      formData.append("csrfmiddlewaretoken", this.getCsrfToken());

      fetch(urls.botSettingsUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            const msg = this.currentBotId
              ? "Bot updated successfully"
              : "Bot added successfully";
            const type = this.currentBotId ? "update" : "success";
            sessionStorage.setItem(
              "toastMessage",
              JSON.stringify({ message: msg, type: type })
            );
            setTimeout(() => window.location.reload(), 1000);
          } else {
            const action = this.currentBotId ? "update" : "add";
            let errorMsg = data.error || `Failed to ${action} bot`;

            if (data.errors) {
              // If we have field-specific errors, join them
              const messages = Object.values(data.errors).flat();
              if (messages.length > 0) {
                errorMsg = messages.join("\n");
              }
            }
            showToast(errorMsg, "error");
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error saving bot", "error");
        });
    },

    deleteBot(botId) {
      this.botToDelete = botId;
      this.showDeleteConfirm = true;
    },

    confirmDelete() {
      if (!this.botToDelete) return;

      const formData = new FormData();
      formData.append("action", "delete");
      formData.append("bot_id", this.botToDelete);
      formData.append("csrfmiddlewaretoken", this.getCsrfToken());

      fetch(urls.botSettingsUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          this.showDeleteConfirm = false;
          this.botToDelete = null;

          if (data.success) {
            sessionStorage.setItem(
              "toastMessage",
              JSON.stringify({
                message: data.message || "Bot deleted successfully",
                type: "success",
              })
            );
            setTimeout(() => window.location.reload(), 1000);
          } else {
            showToast(data.error || "Failed to delete bot", "error");
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error deleting bot", "error");
        });
    },

    testConnection(botId) {
      showToast("Testing connection...", "info");

      const formData = new FormData();
      formData.append("bot_id", botId);
      formData.append("csrfmiddlewaretoken", this.getCsrfToken());

      fetch(urls.testConnectionUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            showToast(
              data.message || "Connection test successful",
              "success"
            );
          } else {
            showToast(data.error || "Connection test failed", "error");
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error testing connection", "error");
        });
    },

    connectBot(botId) {
      showToast("Connecting bot...", "info");

      const formData = new FormData();
      formData.append("bot_id", botId);
      formData.append("csrfmiddlewaretoken", this.getCsrfToken());

      fetch(urls.connectBotUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            sessionStorage.setItem(
              "toastMessage",
              JSON.stringify({
                message: data.message || "Bot connected successfully",
                type: "success",
              })
            );
            setTimeout(() => window.location.reload(), 1000);
          } else {
            showToast(data.error || "Failed to connect bot", "error");
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error connecting bot", "error");
        });
    },

    disconnectBot(botId) {
      showToast("Disconnecting bot...", "info");

      const formData = new FormData();
      formData.append("bot_id", botId);
      formData.append("csrfmiddlewaretoken", this.getCsrfToken());

      fetch(urls.disconnectBotUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            sessionStorage.setItem(
              "toastMessage",
              JSON.stringify({
                message: data.message || "Bot disconnected successfully",
                type: "success",
              })
            );
            setTimeout(() => window.location.reload(), 1000);
          } else {
            showToast(data.error || "Failed to disconnect bot", "error");
          }
        })
        .catch((err) => {
          console.error(err);
          showToast("Error disconnecting bot", "error");
        });
    },
  };
};
