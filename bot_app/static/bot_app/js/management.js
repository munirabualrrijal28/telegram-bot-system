// Management Page JavaScript - Category and FAQ Management
// NOTE: Django URLs are passed via data attributes in HTML

// Global state variables
let currentCategoryId = null;
let deleteCategoryId = null;
let currentFaqId = null;
let currentViewedRootId = null;
let openModalsCount = 0;
let deleteFaqId = null;

// URLs object - will be initialized from HTML data attributes
let urls = {};

// Initialize URLs from data attributes
function initializeManagementJS(urlConfig) {
  urls = urlConfig;
}

// CSRF Token Helper
function getCsrf() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";").map((c) => c.trim());
  for (let c of cookies) {
    if (c.startsWith(name + "=")) return decodeURIComponent(c.split("=")[1]);
  }
  return "";
}

// Modal toggle functions with proper tracking
function showModal(id) {
  const modal = document.getElementById(id);
  if (modal.classList.contains("hidden")) {
    modal.classList.remove("hidden");
    openModalsCount++;
    document.body.style.overflow = "hidden";
  }
}

function hideModal(id) {
  const modal = document.getElementById(id);
  if (!modal.classList.contains("hidden")) {
    modal.classList.add("hidden");
    openModalsCount--;
    if (openModalsCount <= 0) {
      openModalsCount = 0;
      document.body.style.overflow = "";
    }
  }
}

// Category Modal Functions
function openAddCategoryModal() {
  currentCategoryId = null;
  document.getElementById("categoryModalLabel").textContent = "Add Category";
  document.getElementById("categoryId").value = "";
  document.getElementById("categoryName").value = "";
  showModal("categoryModal");
}

function openEditCategoryModal(id, name) {
  currentCategoryId = id;
  document.getElementById("categoryModalLabel").textContent = "Edit Category";
  document.getElementById("categoryId").value = id;
  document.getElementById("categoryName").value = name;
  showModal("categoryModal");
}

function closeCategoryModal() {
  hideModal("categoryModal");
}

// Subcategory Modal Functions
function openAddSubcategoryModal(parentId) {
  document.getElementById("subcategoryModalLabel").textContent =
    "Add Subcategory";
  document.getElementById("subcategoryParentId").value = parentId;
  document.getElementById("subcategoryName").value = "";
  showModal("subcategoryModal");
}

function closeSubcategoryModal() {
  hideModal("subcategoryModal");
}

// FAQ Modal Functions
function openAddFaqModal(categoryId) {
  currentFaqId = null;
  document.getElementById("faqModalLabel").textContent = "Add FAQ";
  document.getElementById("faqId").value = "";
  document.getElementById("faqCategoryId").value = categoryId;
  document.getElementById("faqQuestion").value = "";
  document.getElementById("faqAnswer").value = "";
  document.getElementById("faqIsActive").checked = true;
  showModal("faqModal");
}

function openEditFaqModal(faqId) {
  const url = urls.faqDetail.replace(
    "00000000-0000-0000-0000-000000000000",
    faqId
  );

  fetch(url, {
    credentials: "same-origin",
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((res) => res.json())
    .then((data) => {
      currentFaqId = data.id;
      document.getElementById("faqModalLabel").textContent = "Edit FAQ";
      document.getElementById("faqId").value = data.id;
      document.getElementById("faqCategoryId").value = data.category_id || "";
      document.getElementById("faqQuestion").value = data.question || "";
      document.getElementById("faqAnswer").value = data.answer || "";
      document.getElementById("faqIsActive").checked = data.is_active || false;
      showModal("faqModal");
    })
    .catch((err) => {
      console.error(err);
      alert("Failed to load FAQ details");
    });
}

function closeFaqModal() {
  hideModal("faqModal");
}

// Delete Modal Functions
function openDeleteConfirmModal(id, name) {
  deleteCategoryId = id;
  document.getElementById("deleteCategoryName").textContent = name;
  showModal("deleteModal");
}

function closeDeleteModal() {
  hideModal("deleteModal");
}

function closeViewModal() {
  hideModal("viewModal");
}

// Form Submit Functions
function submitCategoryForm() {
  const name = document.getElementById("categoryName").value.trim();
  if (!name) {
    alert("Category name is required");
    return;
  }

  const isEdit = !!currentCategoryId;
  const url = isEdit
    ? urls.categoryUpdate.replace(
        "00000000-0000-0000-0000-000000000000",
        currentCategoryId
      )
    : urls.categoryCreate;

  const formData = new FormData();
  formData.append("name", name);

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        closeCategoryModal();
        const msg = isEdit
          ? "Category updated successfully"
          : "Category added successfully";
        const type = isEdit ? "update" : "success";

        if (
          currentViewedRootId &&
          !document.getElementById("viewModal").classList.contains("hidden")
        ) {
          if (currentCategoryId === currentViewedRootId) {
            document.getElementById("viewModalTitle").textContent = name;
          }
          openViewModal(
            currentViewedRootId,
            document.getElementById("viewModalTitle").textContent
          );
          showToast(msg, type);
        } else {
          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({ message: msg, type: type })
          );
          location.reload();
        }
      } else {
        const action = isEdit ? "update" : "add";
        showToast(data.error || `Failed to ${action} category`, "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });

    
}

function submitSubcategoryForm() {
  const name = document.getElementById("subcategoryName").value.trim();
  const parentId = document.getElementById("subcategoryParentId").value;

  if (!name) {
    alert("Subcategory name is required");
    return;
  }

  const formData = new FormData();
  formData.append("name", name);
  formData.append("parent_id", parentId);

  fetch(urls.categoryCreate, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        closeSubcategoryModal();
        const msg = "Subcategory added successfully";

        if (currentViewedRootId) {
          openViewModal(
            currentViewedRootId,
            document.getElementById("viewModalTitle").textContent
          );
          showToast(msg);
        } else {
          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({ message: msg, type: "success" })
          );
          location.reload();
        }
      } else {
        showToast(data.error || "Failed to add subcategory", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });
}

function submitFaqForm() {
  const question = document.getElementById("faqQuestion").value.trim();
  const answer = document.getElementById("faqAnswer").value.trim();
  const categoryId = document.getElementById("faqCategoryId").value;
  const isActive = document.getElementById("faqIsActive").checked;

  if (!question) {
    alert("Question is required");
    return;
  }

  const isEdit = !!currentFaqId;
  const url = isEdit
    ? urls.faqUpdate.replace(
        "00000000-0000-0000-0000-000000000000",
        currentFaqId
      )
    : urls.faqCreate;

  const formData = new FormData();
  formData.append("question", question);
  formData.append("answer", answer);
  if (categoryId) formData.append("category_id", categoryId);
  formData.append("is_active", isActive ? "true" : "false");

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        closeFaqModal();
        const msg = currentFaqId
          ? "FAQ updated successfully"
          : "FAQ added successfully";
        const type = currentFaqId ? "update" : "success";

        if (
          !document
            .getElementById("viewModal")
            .classList.contains("hidden") &&
          currentViewedRootId
        ) {
          openViewModal(
            currentViewedRootId,
            document.getElementById("viewModalTitle").textContent
          );
          showToast(msg, type);
        } else {
          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({ message: msg, type: type })
          );
          location.reload();
        }
      } else {
        const action = currentFaqId ? "update" : "add";
        showToast(data.error || `Failed to ${action} FAQ`, "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });
}

// Delete Functions
function deleteCategory(id) {
  const url = urls.categoryDelete.replace(
    "00000000-0000-0000-0000-000000000000",
    id
  );

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        closeDeleteModal();
        if (
          currentViewedRootId &&
          !document.getElementById("viewModal").classList.contains("hidden")
        ) {
          if (id === currentViewedRootId) {
            closeViewModal();
            sessionStorage.setItem(
              "toastMessage",
              JSON.stringify({
                message: "Category deleted successfully",
                type: "success",
              })
            );
            location.reload();
          } else {
            openViewModal(
              currentViewedRootId,
              document.getElementById("viewModalTitle").textContent
            );
            showToast("Category deleted successfully");
          }
        } else {
          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({
              message: "Category deleted successfully",
              type: "success",
            })
          );
          location.reload();
        }
      } else {
        showToast(data.error || "Failed to delete category", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });
}

function deleteFaq(id) {
  deleteFaqId = id;
  document.getElementById("deleteFaqName").textContent = "this FAQ";
  showModal("deleteFaqModal");
}

function confirmDeleteFaq() {
  if (!deleteFaqId) return;

  const url = urls.faqDelete.replace(
    "00000000-0000-0000-0000-000000000000",
    deleteFaqId
  );

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        hideModal("deleteFaqModal");
        if (
          currentViewedRootId &&
          !document.getElementById("viewModal").classList.contains("hidden")
        ) {
          openViewModal(
            currentViewedRootId,
            document.getElementById("viewModalTitle").textContent
          );
          showToast("FAQ deleted successfully");
        } else {
          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({
              message: "FAQ deleted successfully",
              type: "success",
            })
          );
          location.reload();
        }
      } else {
        showToast(data.error || "Failed to delete FAQ", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });
}

function toggleFaqStatus(faqId) {
  const url = urls.toggleFaqStatus.replace(
    "00000000-0000-0000-0000-000000000000",
    faqId
  );

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        if (currentViewedRootId) {
          openViewModal(
            currentViewedRootId,
            document.getElementById("viewModalTitle").textContent
          );
          showToast("FAQ status updated successfully", "update");
        }
      } else {
        showToast(data.error || "Failed to update FAQ status", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Server error", "error");
    });
}

// View Modal Functions
function openViewModal(categoryId, categoryName) {
  currentViewedRootId = categoryId;
  document.getElementById("viewModalTitle").textContent = categoryName;
  document.getElementById("viewModalContent").innerHTML =
    '<div class="text-center text-gray-500 py-10">Loading...</div>';
  showModal("viewModal");

  const url = urls.faqListPartial.replace(
    "00000000-0000-0000-0000-000000000000",
    categoryId
  );

  fetch(url, {
    credentials: "same-origin",
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("viewModalContent").innerHTML = data.html;
        attachViewModalHandlers();
      } else {
        // Show the actual server error to help with debugging
        const errorMsg = data.error || "Unknown error";
        document.getElementById("viewModalContent").innerHTML =
          `<div class="p-4 text-red-500"><strong>Failed to load content</strong><br><code class="text-xs text-red-400 mt-2 block">${errorMsg}</code></div>`;
        console.error("Tree view error:", errorMsg);
      }
    })
    .catch((err) => {
      console.error(err);
      document.getElementById("viewModalContent").innerHTML =
        `<div class="p-4 text-red-500">Network error loading content. <code class="text-xs block">${err}</code></div>`;
    });
}

function attachViewModalHandlers() {
  const content = document.getElementById("viewModalContent");
  content.addEventListener("click", function (e) {
    const button = e.target.closest("[data-action]");
    if (!button) return;

    const action = button.getAttribute("data-action");
    const categoryId = button.getAttribute("data-category-id");
    const faqId = button.getAttribute("data-faq-id");
    const categoryName = button.getAttribute("data-category-name");

    if (action === "add-subcategory") {
      openAddSubcategoryModal(categoryId);
    } else if (action === "add-question") {
      openAddFaqModal(categoryId);
    } else if (action === "edit-category") {
      openEditCategoryModal(categoryId, categoryName);
    } else if (action === "delete-category") {
      openDeleteConfirmModal(categoryId, categoryName);
    } else if (action === "edit-question") {
      openEditFaqModal(faqId);
    } else if (action === "delete-question") {
      deleteFaq(faqId);
    } else if (action === "toggle-status") {
      toggleFaqStatus(faqId);
    } else if (action === "add-page") {
      openAddPageModal(categoryId);
    } else if (action === "edit-page") {
      // We need to pass name via data attribute or fetch it
      // For simplicity, let's assume the button has data-page-name
      const pageName = button.getAttribute("data-page-name");
      openEditPageModal(button.getAttribute("data-page-id"), pageName);
    } else if (action === "delete-page") {
      if(confirm("Are you sure you want to delete this page?")) {
          deletePage(button.getAttribute("data-page-id"));
      }
    } else if (action === "add-group") {
      openAddGroupModal(button.getAttribute("data-page-id"));
    } else if (action === "delete-group") {
      if(confirm("Are you sure you want to delete this group?")) {
          deleteGroup(button.getAttribute("data-group-id"));
      }
    } else if (action === "preview-page") {
      openPreviewModal(button.getAttribute("data-page-id"));
    }
  });
}

// --- Page Functions ---

let currentPageId = null;

function openAddPageModal(categoryId) {
    currentPageId = null;
    document.getElementById("pageModalLabel").textContent = "Add Page";
    document.getElementById("pageId").value = "";
    document.getElementById("pageCategoryId").value = categoryId;
    document.getElementById("pageName").value = "";
    showModal("pageModal");
}

function openEditPageModal(pageId, name) {
    currentPageId = pageId;
    document.getElementById("pageModalLabel").textContent = "Edit Page";
    document.getElementById("pageId").value = pageId;
    document.getElementById("pageName").value = name;
    showModal("pageModal");
}

function closePageModal() {
    hideModal("pageModal");
}

function submitPageForm() {
    const name = document.getElementById("pageName").value.trim();
    const categoryId = document.getElementById("pageCategoryId").value;
    
    if (!name) { alert("Page name is required"); return; }
    
    const isEdit = !!currentPageId;
    const url = isEdit 
        ? urls.pageUpdate.replace("00000000-0000-0000-0000-000000000000", currentPageId)
        : urls.pageCreate;
        
    const formData = new FormData();
    formData.append("name", name);
    if (!isEdit) formData.append("category_id", categoryId);
    
    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrf(), "X-Requested-With": "XMLHttpRequest" },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closePageModal();
            refreshCategoryView();
            showToast(isEdit ? "Page updated" : "Page added", "success");
        } else {
            showToast(data.error || "Failed", "error");
        }
    });
}

let deletePageId = null;

function deletePage(pageId) {
    deletePageId = pageId;
    // Try to get page name from the DOM if possible, otherwise just show "this page"
    const pageElement = document.getElementById(`page-${pageId}`);
    const pageName = pageElement ? pageElement.querySelector('.font-medium').textContent : "this page";
    document.getElementById("deletePageName").textContent = pageName;
    showModal("deletePageModal");
}

function confirmDeletePage() {
    if (!deletePageId) return;

    const url = urls.pageDelete.replace("00000000-0000-0000-0000-000000000000", deletePageId);
    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrf(), "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            hideModal("deletePageModal");
            refreshCategoryView();
            showToast("Page deleted", "success");
        } else {
            showToast(data.error || "Failed", "error");
        }
    });
}

// --- Group Functions ---

let currentAttachmentTab = 'general';
let allAttachments = { general: [], medicines: [] };
let selectedAttachmentIds = new Set();

function openAddGroupModal(pageId) {
    document.getElementById("groupPageId").value = pageId;
    document.getElementById("groupId").value = ""; // Clear group ID for new group
    document.getElementById("groupName").value = "";
    document.getElementById("groupBotUsername").value = "";
    document.getElementById("groupImage").value = "";
    document.getElementById("groupImagePreview").classList.add("hidden");
    document.getElementById("groupImagePlaceholder").classList.remove("hidden");
    document.querySelector("#groupForm button[type='submit']").textContent = "Create Group";
    
    selectedAttachmentIds.clear();
    updateSelectedAttachmentsUI();
    
    // Fetch attachments
    const botId = document.getElementById("currentBotId") ? document.getElementById("currentBotId").value : "";
    fetch(urls.getAttachments + `?page_id=${pageId}&bot_id=${botId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allAttachments.general = data.general;
                allAttachments.medicines = data.medicines;
                renderAttachmentsList();
            }
        });
        
    showModal("groupModal");
}

function openEditGroupModal(groupId, pageId) {
    document.getElementById("groupPageId").value = pageId;
    document.getElementById("groupId").value = groupId;
    document.querySelector("#groupForm button[type='submit']").textContent = "Update Group";
    
    // Fetch group details
    const url = urls.groupDetail.replace("00000000-0000-0000-0000-000000000000", groupId);
    
    // Fetch attachments first
    const botId = document.getElementById("currentBotId") ? document.getElementById("currentBotId").value : "";
    fetch(urls.getAttachments + `?page_id=${pageId}&bot_id=${botId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allAttachments.general = data.general;
                allAttachments.medicines = data.medicines;
                
                // Then fetch group details
                return fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById("groupId").value = data.id;
                document.getElementById("groupName").value = data.name;
                document.getElementById("groupBotUsername").value = data.contact_bot_username || "";
                
                if (data.image_url) {
                    const preview = document.getElementById("groupImagePreview");
                    preview.querySelector("img").src = data.image_url;
                    preview.classList.remove("hidden");
                    document.getElementById("groupImagePlaceholder").classList.add("hidden");
                } else {
                    document.getElementById("groupImagePreview").classList.add("hidden");
                    document.getElementById("groupImagePlaceholder").classList.remove("hidden");
                }
                
                selectedAttachmentIds = new Set(data.attachment_ids);
                updateSelectedAttachmentsUI();
                renderAttachmentsList();
                
                showModal("groupModal");
            } else {
                showToast(data.error || "Failed to load group details", "error");
            }
        });
}

function closeGroupModal() {
    hideModal("groupModal");
}

function previewGroupImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById("groupImagePreview");
            preview.querySelector("img").src = e.target.result;
            preview.classList.remove("hidden");
            document.getElementById("groupImagePlaceholder").classList.add("hidden");
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function switchAttachmentTab(tab) {
    currentAttachmentTab = tab;
    document.getElementById("tab-general").className = tab === 'general' 
        ? "flex-1 px-4 py-2 text-sm font-medium rounded-md bg-white text-gray-900 shadow-sm transition-all"
        : "flex-1 px-4 py-2 text-sm font-medium rounded-md text-gray-500 hover:text-gray-900 transition-all";
        
    document.getElementById("tab-medicines").className = tab === 'medicines'
        ? "flex-1 px-4 py-2 text-sm font-medium rounded-md bg-white text-gray-900 shadow-sm transition-all"
        : "flex-1 px-4 py-2 text-sm font-medium rounded-md text-gray-500 hover:text-gray-900 transition-all";
        
    renderAttachmentsList();
}

function renderAttachmentsList() {
    const container = document.getElementById("attachmentsList");
    const search = document.getElementById("attachmentSearch").value.toLowerCase();
    const items = allAttachments[currentAttachmentTab].filter(item => 
        item.title.toLowerCase().includes(search)
    );
    
    if (items.length === 0) {
        container.innerHTML = '<div class="text-center text-gray-500 py-8">No attachments found</div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="flex items-center p-2 hover:bg-gray-50 rounded border border-gray-100 cursor-pointer" onclick="toggleAttachment('${item.id}', '${item.title.replace(/'/g, "\\'")}')">
            <input type="checkbox" ${selectedAttachmentIds.has(item.id) ? 'checked' : ''} class="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500 pointer-events-none">
            <div class="ml-3 flex-1">
                <p class="text-sm font-medium text-gray-900">${item.title}</p>
                <p class="text-xs text-gray-500">${item.created_at}</p>
            </div>
            ${item.file_url ? `<img src="${item.file_url}" class="w-8 h-8 object-cover rounded" />` : ''}
        </div>
    `).join('');
}

function filterAttachments() {
    renderAttachmentsList();
}

function toggleAttachment(id, title) {
    if (selectedAttachmentIds.has(id)) {
        selectedAttachmentIds.delete(id);
    } else {
        selectedAttachmentIds.add(id);
    }
    renderAttachmentsList(); // Re-render to update checkboxes
    updateSelectedAttachmentsUI();
}

function updateSelectedAttachmentsUI() {
    const container = document.getElementById("selectedAttachments");
    document.getElementById("selectedCount").textContent = selectedAttachmentIds.size;
    
    if (selectedAttachmentIds.size === 0) {
        container.innerHTML = '<p class="text-sm text-gray-400 w-full text-center py-2">No attachments selected yet</p>';
        return;
    }
    
    // Find details for selected IDs
    const selectedItems = [];
    [...allAttachments.general, ...allAttachments.medicines].forEach(item => {
        if (selectedAttachmentIds.has(item.id)) selectedItems.push(item);
    });
    
    container.innerHTML = selectedItems.map(item => `
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-white border border-gray-200 text-sm shadow-sm">
            ${item.title}
            <button type="button" onclick="toggleAttachment('${item.id}')" class="text-gray-400 hover:text-red-500 ml-1">×</button>
        </span>
    `).join('');
}

function submitGroupForm() {
    const name = document.getElementById("groupName").value.trim();
    const pageId = document.getElementById("groupPageId").value;
    const groupId = document.getElementById("groupId").value;
    const imageInput = document.getElementById("groupImage");
    
    const contactBotUsername = document.getElementById("groupBotUsername").value.trim();
    
    if (!name) { alert("Group name is required"); return; }
    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("contact_bot_username", contactBotUsername);
    formData.append("page_id", pageId);
    if (imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
    }
    
    selectedAttachmentIds.forEach(id => {
        formData.append("attachment_ids[]", id);
    });
    
    const url = groupId 
        ? urls.groupUpdate.replace("00000000-0000-0000-0000-000000000000", groupId)
        : urls.groupCreate;
    
    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrf(), "X-Requested-With": "XMLHttpRequest" },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closeGroupModal();
            refreshCategoryView();
            showToast(groupId ? "Group updated successfully" : "Group created successfully", "success");
        } else {
            showToast(data.error || "Failed", "error");
        }
    })
    .catch(err => {
    });
}

let deleteGroupId = null;

function deleteGroup(groupId) {
    deleteGroupId = groupId;
    // Try to find group name
    const groupElement = document.querySelector(`button[onclick="deleteGroup('${groupId}')"]`);
    let groupName = "this group";
    if (groupElement) {
        const nameEl = groupElement.closest('.bg-white').querySelector('h5');
        if (nameEl) groupName = nameEl.textContent;
    }
    document.getElementById("deleteGroupName").textContent = groupName;
    showModal("deleteGroupModal");
}

function confirmDeleteGroup() {
    if (!deleteGroupId) return;

    const url = urls.groupDelete.replace("00000000-0000-0000-0000-000000000000", deleteGroupId);
    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrf(), "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            hideModal("deleteGroupModal");
            refreshCategoryView();
            showToast("Group deleted", "success");
        } else {
            showToast(data.error || "Failed", "error");
        }
    });
}

function refreshCategoryView() {
    try {
        if (currentViewedRootId) {
            const titleEl = document.getElementById("viewModalTitle");
            if (titleEl) {
                openViewModal(currentViewedRootId, titleEl.textContent);
            } else {
                console.warn("viewModalTitle element not found");
            }
        }
    } catch (e) {
        console.error("Error in refreshCategoryView:", e);
    }
}

// Event Listeners
document.addEventListener("DOMContentLoaded", function () {
  // Category Form Submit
  const categoryForm = document.getElementById("categoryForm");
  if (categoryForm) {
      categoryForm.addEventListener("submit", function (e) {
          e.preventDefault();
          submitCategoryForm();
      });
  }

  // Subcategory Form Submit
  const subcategoryForm = document.getElementById("subcategoryForm");
  if (subcategoryForm) {
      subcategoryForm.addEventListener("submit", function (e) {
          e.preventDefault();
          submitSubcategoryForm();
      });
  }

  // FAQ Form Submit
  const faqForm = document.getElementById("faqForm");
  if (faqForm) {
      faqForm.addEventListener("submit", function (e) {
        e.preventDefault();
        submitFaqForm();
      });
  }

  // Page Form Submit
  const pageForm = document.getElementById("pageForm");
  if (pageForm) {
      pageForm.addEventListener("submit", function (e) {
        e.preventDefault();
        submitPageForm();
      });
  }

  // Group Form Submit
  const groupForm = document.getElementById("groupForm");
  if (groupForm) {
      groupForm.addEventListener("submit", function (e) {
        e.preventDefault();
        submitGroupForm();
      });
  }

  // Confirm Delete Category
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", function () {
        if (deleteCategoryId) {
          deleteCategory(deleteCategoryId);
        }
      });
  }

  // Confirm Delete FAQ
  const confirmDeleteFaqBtn = document.getElementById("confirmDeleteFaqBtn");
  if (confirmDeleteFaqBtn) {
      confirmDeleteFaqBtn.addEventListener("click", function () {
        confirmDeleteFaq();
      });
  }
});

// Live Preview Toggle
// Live Preview Toggle
// Live Preview Toggle
function togglePreviewStyle(style, save = true) {
  try {
      const inlineContainer = document.getElementById("inlineButtonsContainer");
      const replyContainer = document.getElementById("replyKeyboardContainer");
      const btnInline = document.getElementById("btn-style-inline");
      const btnReply = document.getElementById("btn-style-reply");

      // Check if we are already in the requested mode to avoid unnecessary processing
      // REMOVED OPTIMIZATION: It was causing issues with state synchronization.
      // We will force the update every time.


      // Update Button States
      const activeClass = "px-4 py-2 text-sm font-medium rounded-md transition-all bg-blue-500 text-white hover:bg-blue-600 shadow-sm";
      const inactiveClass = "px-4 py-2 text-sm font-medium rounded-md transition-all bg-white text-gray-900 shadow-sm border border-gray-200 hover:bg-gray-50";

      if (style === "REPLY") {
          if (btnReply) btnReply.className = activeClass;
          if (btnInline) btnInline.className = inactiveClass;
      } else {
          if (btnInline) btnInline.className = activeClass;
          if (btnReply) btnReply.className = inactiveClass;
      }
      
      // Get all buttons (we'll move them around)
      let buttons = [];
      if (inlineContainer.children.length > 0) {
        buttons = Array.from(inlineContainer.children);
      } else {
        buttons = Array.from(replyContainer.children);
      }

      if (style === "REPLY") {
        // Switch to Reply Mode
        inlineContainer.classList.add("hidden");
        replyContainer.classList.remove("hidden");
        
        // Move buttons to reply container and adjust styling
        buttons.forEach(btn => {
          // Remove inline specific classes
          btn.className = "bg-white border border-gray-300 rounded-lg px-2 py-2 text-center text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 truncate";
          // Remove the icon/flex structure for simpler reply button look
          const textSpan = btn.querySelector("span.text-sm");
          if (textSpan) {
              btn.textContent = textSpan.textContent.trim();
          }
          replyContainer.appendChild(btn);
        });
        
      } else {
        // Switch to Inline Mode
        replyContainer.classList.add("hidden");
        inlineContainer.classList.remove("hidden");
        
        // Move buttons back to inline container and restore styling
        buttons.forEach(btn => {
          btn.className = "w-full bg-white border border-gray-200 hover:border-primary-500 hover:bg-primary-50 rounded-lg px-4 py-2 text-left transition-all";
          // Restore icon structure
          const text = btn.textContent.trim();
          btn.innerHTML = `
            <div class="flex items-center gap-2">
              <span class="text-lg">📁</span>
              <span class="text-sm font-medium text-gray-800">${text}</span>
            </div>
          `;
          inlineContainer.appendChild(btn);
        });
      }

      // Save to server if requested
      if (save) {
          saveKeyboardPreference(style);
      }
  } catch (e) {
      console.error("Error in togglePreviewStyle:", e);
      alert("Error switching style: " + e.message);
  }
}

function saveKeyboardPreference(style) {
  console.log("saveKeyboardPreference called with:", style);
  console.log("Current urls object:", urls);

  if (urls && urls.updateKeyboardType) {
      fetch(urls.updateKeyboardType, {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrf(),
          },
          body: JSON.stringify({ keyboard_type: style }),
      })
      .then(response => {
          if (!response.ok) {
              throw new Error("Network response was not ok");
          }
          return response.json();
      })
      .then(data => {
          console.log("Server response:", data);
          if (data.success) {
              console.log("Keyboard preference saved successfully. New type:", data.keyboard_type);
          } else {
              console.error("Failed to save keyboard preference", data.error);
              alert("Failed to save keyboard preference: " + data.error);
          }
      })
      .catch(error => {
          console.error("Error saving keyboard preference:", error);
          alert("Error saving keyboard preference: " + error);
      });
  } else {
      console.error("updateKeyboardType URL not found. urls:", urls);
      alert("Configuration error: updateKeyboardType URL missing. Check console.");
  }
}

// --- Preview Modal Functions ---

let previewHistory = [];
let currentPreviewPageData = null;

function openPreviewModal(pageId) {
    const script = document.getElementById(`preview-data-${pageId}`);
    if (!script) {
        showToast("Error: Preview data not found", "error");
        return;
    }
    
    try {
        currentPreviewPageData = JSON.parse(script.textContent);
        previewHistory = [];
        showModal("previewModal");
        renderPreviewPage(currentPreviewPageData);
    } catch (e) {
        console.error("Error parsing preview data", e);
        showToast("Error loading preview", "error");
    }
}

function closePreviewModal() {
    hideModal("previewModal");
    previewHistory = [];
    currentPreviewPageData = null;
}

function handlePreviewBack() {
    if (previewHistory.length > 0) {
        const previousState = previewHistory.pop();
        if (previousState) {
            if (previousState.type === 'page') {
                renderPreviewPage(previousState.data, false);
            } else if (previousState.type === 'group') {
                renderPreviewGroup(previousState.data, false);
            }
        }
    }
}

function updatePreviewHeader(title, showBack) {
    document.getElementById("previewTitle").textContent = title;
    const backBtn = document.getElementById("previewBackBtn");
    if (showBack) {
        backBtn.classList.remove("hidden");
    } else {
        backBtn.classList.add("hidden");
    }
}

function renderPreviewPage(pageData, pushToHistory = true) {
    updatePreviewHeader(pageData.name, false);
    const content = document.getElementById("previewContent");
    
    if (!pageData.groups || pageData.groups.length === 0) {
        content.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-gray-400">
                <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                <p>No groups in this page</p>
            </div>
        `;
        return;
    }

    content.innerHTML = `
        <div class="grid grid-cols-2 gap-3">
            ${pageData.groups.map(group => `
                <div onclick="navigateToGroup('${group.id}')" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:shadow-md transition-shadow active:scale-95 transform duration-150">
                    <div class="aspect-square bg-gray-100 relative">
                        ${group.image_url 
                            ? `<img src="${group.image_url}" class="w-full h-full object-cover" />`
                            : `<div class="w-full h-full flex items-center justify-center text-gray-300"><svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>`
                        }
                        <div class="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm">
                            ${group.items ? group.items.length : 0} items
                        </div>
                    </div>
                    <div class="p-3">
                        <h4 class="font-bold text-gray-800 text-sm truncate">${group.name}</h4>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function navigateToGroup(groupId) {
    const group = currentPreviewPageData.groups.find(g => g.id === groupId);
    if (group) {
        previewHistory.push({ type: 'page', data: currentPreviewPageData });
        renderPreviewGroup(group);
    }
}

function renderPreviewGroup(groupData, pushToHistory = true) {
    updatePreviewHeader(groupData.name, true);
    const content = document.getElementById("previewContent");
    
    if (!groupData.items || groupData.items.length === 0) {
        content.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-gray-400">
                <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
                <p>No items in this group</p>
            </div>
        `;
        return;
    }

    content.innerHTML = `
        <div class="grid grid-cols-2 gap-3">
            ${groupData.items.map(item => `
                <div onclick="navigateToItem('${groupData.id}', '${item.id}')" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:shadow-md transition-shadow active:scale-95 transform duration-150">
                    <div class="aspect-square bg-gray-100 relative">
                        ${item.image_url 
                            ? `<img src="${item.image_url}" class="w-full h-full object-cover" />`
                            : `<div class="w-full h-full flex items-center justify-center text-gray-300"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg></div>`
                        }
                    </div>
                    <div class="p-3">
                        <h4 class="font-medium text-gray-800 text-xs line-clamp-2 leading-tight h-8">${item.title}</h4>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function navigateToItem(groupId, itemId) {
    const group = currentPreviewPageData.groups.find(g => g.id === groupId);
    if (group) {
        const item = group.items.find(i => i.id === itemId);
        if (item) {
            previewHistory.push({ type: 'group', data: group });
            renderPreviewItem(item);
        }
    }
}

function renderPreviewItem(itemData, pushToHistory = true) {
    updatePreviewHeader(itemData.title, true);
    const content = document.getElementById("previewContent");
    
    // Determine which bot username to use:
    // 1. Group specific (if available)
    // 2. Page/Bot default (fallback)
    // We need to find the current group to check its setting
    let botUsername = currentPreviewPageData.bot_username;
    if (previewHistory.length > 0) {
        // The last item in history should be the group
        const lastState = previewHistory[previewHistory.length - 1];
        if (lastState.type === 'group' && lastState.data.contact_bot_username) {
            botUsername = lastState.data.contact_bot_username;
        }
    }

    content.innerHTML = `
        <div class="space-y-4">
            <div class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100">
                <div class="aspect-video bg-gray-100 relative">
                    ${itemData.image_url 
                        ? `<img src="${itemData.image_url}" class="w-full h-full object-cover" />`
                        : `<div class="w-full h-full flex items-center justify-center text-gray-300"><svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>`
                    }
                </div>
                <div class="p-5">
                    <h2 class="text-xl font-bold text-gray-900 mb-1">${itemData.title}</h2>
                    <p class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-4">${itemData.type === 'medicine' ? 'Product' : 'General'}</p>
                    
                    <div class="prose prose-sm text-gray-600">
                        <p>${itemData.description && itemData.description !== 'None' ? itemData.description : 'No description available.'}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Actions</h4>
                <a href="https://t.me/${botUsername}" target="_blank" class="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500 group-hover:scale-110 transition-transform">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                        </div>
                        <span class="font-medium text-gray-700">Contact Store</span>
                    </div>
                    <div class="flex items-center text-gray-400 text-xs">
                        <span class="mr-1">@${botUsername}</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </div>
                </a>
            </div>
        </div>
    `;
}


function togglePageGroups(pageId) {
    const container = document.getElementById(`groups-container-${pageId}`);
    const chevron = document.getElementById(`chevron-${pageId}`);
    
    // Check if it's currently collapsed (0fr)
    if (container.classList.contains('grid-rows-[0fr]')) {
        container.classList.remove('grid-rows-[0fr]');
        container.classList.add('grid-rows-[1fr]');
        chevron.classList.add('rotate-90');
    } else {
        container.classList.remove('grid-rows-[1fr]');
        container.classList.add('grid-rows-[0fr]');
        chevron.classList.remove('rotate-90');
    }
}
