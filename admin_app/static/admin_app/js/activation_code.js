// Management Page JavaScript - Activation Code Management

// Global state variables
let currentCodeId = null; 
let openModalsCount = 0; 
let urls = {};

// Initialize URLs from data attributes
function initializeCodeJS(urlConfig) {
    urls = urlConfig;
}

// 1. CSRF Token Helper
function getCsrf() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) return csrfInput.value;
    
    const name = "csrftoken";
    try {
        const cookies = document.cookie.split(";").map((c) => c.trim());
        for (let c of cookies) {
            if (c.startsWith(name + "=")) return decodeURIComponent(c.split("=")[1]);
        }
    } catch (e) {}
    return "";
}

// 2. Toast Utility
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return; 

    let color = type === 'error' ? 'bg-red-600' : (type === 'update' ? 'bg-blue-600' : 'bg-green-600');
    const toast = document.createElement('div');
    toast.className = `p-4 rounded-lg text-white shadow-xl max-w-sm transition-all duration-300 transform translate-x-full opacity-0 ${color}`;
    toast.innerHTML = `<p class="font-medium">${message}</p>`;

    container.appendChild(toast);
    setTimeout(() => { toast.classList.remove('translate-x-full', 'opacity-0'); toast.classList.add('translate-x-0', 'opacity-100'); }, 50);
    setTimeout(() => { toast.remove(); }, 4000);
}

// 3. Modal Logic
function showModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("hidden");
}

function hideModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("hidden");
}

function openAddCodeModal() {
    currentCodeId = null; 
    document.getElementById("codeModalLabel").textContent = "Create New Activation Code";
    document.getElementById("codeForm").reset();
    
    // Reset to general code type
    const generalRadio = document.querySelector('input[name="code_type"][value="general"]');
    if (generalRadio) {
        generalRadio.checked = true;
        generalRadio.dispatchEvent(new Event('change'));
    }
    
    showModal("codeModal");
}

function closeCodeModal() {
    hideModal("codeModal");
}

// Open modal for EDITING
function openCodeModal(codeId, element) {
    currentCodeId = codeId; 
    const form = document.getElementById("codeForm");
    
    document.getElementById("codeModalLabel").textContent = `Edit Code: ${element.dataset.code}`;
    form.reset(); 

    // Populate plan
    const planSelect = document.getElementById('id_plan_name');
    if(planSelect) planSelect.value = element.dataset.plan;

    // Handle Code Type Radio Buttons
    const typeValue = element.dataset.type;
    const radios = document.querySelectorAll('input[name="code_type"]');
    radios.forEach(radio => {
        if(radio.value === typeValue) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change')); 
            radio.dispatchEvent(new Event('input')); 
        }
    });

    // Populate target user if exists
    const targetSelect = document.getElementById('id_target_user');
    const targetUserId = element.dataset.targetId;
    if(targetSelect && targetUserId) {
        targetSelect.value = targetUserId;
    }

    // Populate expires date
    const expiresInput = document.getElementById('id_expires_at');
    if(expiresInput && element.dataset.expires) expiresInput.value = element.dataset.expires;

    showModal("codeModal");
}

// 4. Submit Logic
function submitCodeForm() {
    const form = document.getElementById("codeForm");
    const formData = new FormData(form);
    
    let url = currentCodeId ? urls.codeUpdate.replace("/00000000-0000-0000-0000-000000000000/", `/${currentCodeId}/`) : urls.codeCreate;
    let action = currentCodeId ? "updated" : "created";

    if (!formData.get('csrfmiddlewaretoken')) {
        formData.append("csrfmiddlewaretoken", getCsrf());
    }

    fetch(url, {
        method: "POST", 
        credentials: "same-origin",
        headers: { 
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCsrf()
        },
        body: formData,
    })
    .then(res => {
        if (res.ok) {
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return res.json();
            }
            throw new Error("ForceReload");
        }
        return res.text().then(text => { 
            console.error("Server response:", text);
            throw new Error("Server returned error") 
        });
    })
    .then(data => {
        if (data.success) {
            closeCodeModal();
            showToast(`Code ${action} successfully`, "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.message || "Action failed", "error");
        }
    })
    .catch(err => {
        if (err.message === "ForceReload") {
            closeCodeModal();
            showToast(`Code ${action} successfully`, "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            console.error("Error:", err);
            showToast("Server error. Check console for details.", "error");
        }
    });
}

// 5. Delete Logic
function confirmDeleteCode(id, codeValue) {
    if (confirm(`Are you sure you want to delete code: ${codeValue}?`)) {
        deleteCode(id);
    }
}

function deleteCode(id) {
    const url = urls.codeDelete.replace("/00000000-0000-0000-0000-000000000000/", `/${id}/`);
    const csrfToken = getCsrf();
    const bodyData = new URLSearchParams({'csrfmiddlewaretoken': csrfToken});

    fetch(url, {
        method: "POST", 
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: bodyData, 
    })
    .then(res => {
        if(res.ok) {
             const contentType = res.headers.get("content-type");
             if (contentType && contentType.includes("application/json")) return res.json();
             throw new Error("ForceReload");
        }
        return res.text().then(text => {
            console.error("Delete error response:", text);
            throw new Error("Server error");
        });
    })
    .then(data => {
        if (data.success) {
            showToast("Code deleted successfully", "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.error || "Failed to delete code", "error");
        }
    })    .catch(err => {
        if (err.message === "ForceReload") {
            showToast("Code deleted successfully", "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            console.error("Delete error:", err);
            showToast("Deletion failed. Check console for details.", "error");
        }
    });
}

// 6. Listeners
function checkAndDisplayToast() {
    const msg = sessionStorage.getItem("toastMessage");
    if (msg) {
        try {
            const data = JSON.parse(msg);
            setTimeout(() => showToast(data.message, data.type), 100);
            sessionStorage.removeItem("toastMessage");
        } catch(e) {}
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("codeForm");
    if(form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            submitCodeForm();
        });
    }
    checkAndDisplayToast();
});