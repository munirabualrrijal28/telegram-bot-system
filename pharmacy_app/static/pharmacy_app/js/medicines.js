// Medicines Page JavaScript - Medicine CRUD, Import/Export, and File Upload Management
// NOTE: Django template variables are passed via data attributes in HTML

// Define global state object to avoid polluting global namespace too much
window.PharmacyState = {
  pond: null,
  importData: {
    columns: [],
    dbFields: [],
    mapping: {},
    totalRows: 0,
  },
};

console.log("Medicine JS loaded - Global State Initialized");

// Initialize FilePond
window.initFilePond = function (uploadUrl, csrfToken) {
  console.log("initFilePond called");
  try {
    if (typeof FilePond === "undefined") {
      console.warn("FilePond not loaded yet");
      return;
    }

    // Register plugins if available
    try {
      FilePond.registerPlugin(
        FilePondPluginImagePreview,
        FilePondPluginFileValidateType,
        FilePondPluginImageExifOrientation
      );
    } catch (e) {
      console.warn("FilePond plugins not loaded", e);
    }

    const inputElement = document.querySelector("#modalImageInput");
    if (!inputElement) {
      console.log("No #modalImageInput found, skipping FilePond init");
      return;
    }

    // Destroy existing instance if any
    if (window.PharmacyState.pond) {
      FilePond.destroy(inputElement);
    }

    // Check for existing image
    const existingUrlInput = document.getElementById("existingImageUrl");
    const files = [];
    if (existingUrlInput && existingUrlInput.value) {
      files.push({
        source: existingUrlInput.value,
        options: {
          type: "local",
        },
      });
    }

    window.PharmacyState.pond = FilePond.create(inputElement, {
      acceptedFileTypes: ["image/*"],
      allowMultiple: false,
      instantUpload: true,
      files: files,
      server: {
        process: {
          url: uploadUrl,
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
          onload: (responseText) => {
            document.getElementById("modalUploadedFile").value = responseText;
            return responseText;
          },
          onerror: () => showToast("Upload failed", "error"),
        },
        revert: {
          url: uploadUrl,
          method: "DELETE",
          headers: { "X-CSRFToken": csrfToken },
          onload: () => {
            document.getElementById("modalUploadedFile").value = "";
          },
        },
        load: (source, load, error, progress, abort, headers) => {
          // For editing: load existing image
          fetch(source)
            .then((res) => res.blob())
            .then(load)
            .catch((err) => {
              console.error("Failed to load image:", err);
              error("Could not load image");
            });
        },
      },
    });
  } catch (e) {
    console.error("Error initializing FilePond:", e);
  }
};

// Modal Functions
window.openAddMedicineModal = function (medicineAddUrl, formContentHtml) {
  console.log("openAddMedicineModal called");
  const modal = document.getElementById("medicineModal");
  const form = document.getElementById("medicineForm");
  const title = document.getElementById("modalTitle");
  const formContainer = document.getElementById("medicineFormContainer");

  if (!modal) {
    showToast("Error: medicineModal not found in DOM", "error");
    console.error("Error: medicineModal not found in DOM");
    return;
  }

  // Reset state
  title.textContent = "Add New Medicine";
  form.action = medicineAddUrl;
  form.reset();

  // Clear hidden file input
  const hiddenFile = document.getElementById("modalUploadedFile");
  if (hiddenFile) hiddenFile.value = "";

  // Load empty form content
  formContainer.innerHTML = formContentHtml;

  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";

  // Get upload URL and CSRF token from data attributes
  const uploadUrl = modal.dataset.uploadUrl;
  const csrfToken = modal.dataset.csrfToken;

  // Re-init FilePond
  setTimeout(() => window.initFilePond(uploadUrl, csrfToken), 100);
};

window.openEditMedicineModal = function (url) {
  console.log("openEditMedicineModal called with url:", url);
  const modal = document.getElementById("medicineModal");
  const title = document.getElementById("modalTitle");
  const formContainer = document.getElementById("medicineFormContainer");

  if (!modal) {
    showToast("Error: medicineModal not found", "error");
    console.error("Error: medicineModal not found");
    return;
  }

  title.textContent = "Edit Medicine";
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";

  // Show loading state
  formContainer.innerHTML =
    '<div class="p-6 text-center"><p class="text-gray-500">Loading...</p></div>';

  // Fetch form HTML
  fetch(url, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.html) {
        formContainer.innerHTML = data.html;
        const form = document.getElementById("medicineForm");

        // Update form action
        document.getElementById("medicineForm").action = url;

        // Get upload URL and CSRF token from data attributes
        const uploadUrl = modal.dataset.uploadUrl;
        const csrfToken = modal.dataset.csrfToken;

        // Re-init FilePond
        setTimeout(() => window.initFilePond(uploadUrl, csrfToken), 100);
      }
    })
    .catch((err) => {
      console.error(err);
      showToast("Failed to load medicine data", "error");
      window.closeMedicineModal();
    });
};

window.closeMedicineModal = function () {
  const modal = document.getElementById("medicineModal");
  if (modal) modal.classList.add("hidden");
  document.body.style.overflow = "";
};

// Delete Modal
window.openDeleteMedicineModal = function (url, name) {
  console.log("openDeleteMedicineModal called");
  const modal = document.getElementById("deleteMedicineModal");
  const form = document.getElementById("deleteMedicineForm");
  const msg = document.getElementById("deleteConfirmationMsg");

  if (!modal) {
    showToast("Error: deleteMedicineModal not found", "error");
    console.error("Error: deleteMedicineModal not found");
    return;
  }

  form.action = url;
  msg.textContent = `Are you sure you want to delete "${name}"? This action cannot be undone.`;

  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
};

window.closeDeleteMedicineModal = function () {
  const modal = document.getElementById("deleteMedicineModal");
  if (modal) modal.classList.add("hidden");
  document.body.style.overflow = "";
};

// Import Modal Functions
window.openImportModal = function () {
  const modal = document.getElementById("importModal");
  if (modal) {
    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
    // Reset to upload step
    document.getElementById("uploadStep").classList.remove("hidden");
    document.getElementById("mappingStep").classList.add("hidden");
    document.getElementById("uploadStatus").classList.add("hidden");
  } else {
    showToast("Error: importModal not found", "error");
  }
};

window.closeImportModal = function () {
  const modal = document.getElementById("importModal");
  if (modal) modal.classList.add("hidden");
  document.body.style.overflow = "";
  // Reset file input
  const fileInput = document.getElementById("importFileInput");
  if (fileInput) fileInput.value = "";
  window.PharmacyState.importData = {
    columns: [],
    dbFields: [],
    mapping: {},
    totalRows: 0,
  };
};

window.handleFileUpload = function (event, uploadUrl, csrfToken) {
  const file = event.target.files[0];
  if (!file) return;

  const statusEl = document.getElementById("uploadStatus");
  statusEl.textContent = "Uploading and processing file...";
  statusEl.classList.remove("hidden");

  const formData = new FormData();
  formData.append("import_file", file);

  fetch(uploadUrl, {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        window.PharmacyState.importData.columns = data.columns;
        window.PharmacyState.importData.dbFields = data.db_fields;
        window.PharmacyState.importData.totalRows = data.total_rows;

        statusEl.textContent = `File uploaded successfully! Found ${data.total_rows} rows.`;
        statusEl.classList.add("text-green-600");

        // Show mapping step
        document.getElementById("uploadStep").classList.add("hidden");
        document.getElementById("mappingStep").classList.remove("hidden");

        // Build column mapping UI
        const container = document.getElementById("columnMappingContainer");
        container.innerHTML = "";

        data.columns.forEach((col) => {
          const colDiv = document.createElement("div");
          colDiv.className =
            "grid grid-cols-3 gap-4 items-center p-4 bg-gray-50 rounded-lg";

          colDiv.innerHTML = `
                    <div>
                        <p class="font-medium text-gray-900">${col.name}</p>
                        <p class="text-xs text-gray-500">Sample: ${col.sample
                          .slice(0, 2)
                          .join(", ")}</p>
                    </div>
                    <div>
                        <select class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                onchange="handleColumnMapping('${
                                  col.name
                                }', this.value, event)">
                            ${data.db_fields
                              .map(
                                (field) =>
                                  `<option value="${field.value}">${field.label}</option>`
                              )
                              .join("")}
                        </select>
                    </div>
                    <div id="status-${
                      col.name
                    }" class="text-sm text-gray-400">
                        Skipped
                    </div>
                `;

          container.appendChild(colDiv);
        });

        validateMapping();
      } else {
        statusEl.textContent =
          "Upload failed: " + (data.error || "Unknown error");
        statusEl.classList.add("text-red-600");
      }
    })
    .catch((error) => {
      console.error("Upload error:", error);
      statusEl.textContent = "Error uploading file";
      statusEl.classList.add("text-red-600");
    });
};

window.handleColumnMapping = function (fileColumn, dbField, event) {
  const importData = window.PharmacyState.importData;
  // Check if this field is already mapped to another column
  const existingMapping = Object.entries(importData.mapping).find(
    ([col, field]) =>
      field === dbField && col !== fileColumn && dbField !== ""
  );

  if (existingMapping) {
    showToast(
      `The field "${dbField}" is already mapped to column "${existingMapping[0]}". Please choose a different field.`,
      "warning"
    );
    event.target.value = "";
    return;
  }

  if (dbField) {
    importData.mapping[fileColumn] = dbField;
    document.getElementById(
      `status-${fileColumn}`
    ).innerHTML = `<span class="text-green-600">✓ Mapped</span>`;
  } else {
    delete importData.mapping[fileColumn];
    document.getElementById(
      `status-${fileColumn}`
    ).innerHTML = `<span class="text-gray-400">Skipped</span>`;
  }

  validateMapping();
};

window.validateMapping = function () {
  const importData = window.PharmacyState.importData;
  const mappedFields = Object.values(importData.mapping);
  const requiredFields = importData.dbFields
    .filter((f) => f.required)
    .map((f) => f.value);

  const missingRequired = requiredFields.filter(
    (f) => !mappedFields.includes(f)
  );
  const importBtn = document.getElementById("importBtn");

  if (missingRequired.length > 0) {
    importBtn.disabled = true;
    importBtn.classList.add("opacity-50", "cursor-not-allowed");
    importBtn.title = `Missing required fields: ${missingRequired.join(
      ", "
    )}`;
  } else {
    importBtn.disabled = false;
    importBtn.classList.remove("opacity-50", "cursor-not-allowed");
    importBtn.title = "";
  }
};

window.showPreview = function (previewUrl, csrfToken) {
  const previewBtn = document.getElementById("previewBtn");
  previewBtn.disabled = true;
  previewBtn.textContent = "Loading preview...";

  fetch(previewUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken,
    },
    body: `mapping=${encodeURIComponent(
      JSON.stringify(window.PharmacyState.importData.mapping)
    )}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        renderPreviewTable(
          data.preview_data,
          data.mapped_fields,
          data.total_rows
        );
        document.getElementById("previewModal").classList.remove("hidden");
      } else {
        alert("Error loading preview: " + (data.error || "Unknown error"));
      }
    })
    .catch((error) => {
      console.error("Preview error:", error);
      alert("Error loading preview");
    })
    .finally(() => {
      previewBtn.disabled = false;
      previewBtn.textContent = "Preview Data";
    });
};

window.renderPreviewTable = function (data, fields, totalRows) {
  const container = document.getElementById("previewTableContainer");

  let html = `
        <div class="mb-4">
            <p class="text-sm text-gray-600">Showing first 50 rows of ${totalRows} total</p>
        </div>
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
    `;

  fields.forEach((field) => {
    html += `<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">${field}</th>`;
  });

  html += '</tr></thead><tbody class="bg-white divide-y divide-gray-200">';

  data.forEach((row) => {
    html += `<tr class="hover:bg-gray-50">
            <td class="px-4 py-3 text-sm text-gray-500">${row._row_num}</td>`;
    fields.forEach((field) => {
      const value = row[field] || "-";
      html += `<td class="px-4 py-3 text-sm text-gray-900">${value}</td>`;
    });
    html += "</tr>";
  });

  html += "</tbody></table>";
  container.innerHTML = html;
};

window.closePreviewModal = function () {
  const modal = document.getElementById("previewModal");
  if (modal) modal.classList.add("hidden");
};

window.processImport = function (processUrl, csrfToken) {
  const importBtn = document.getElementById("importBtn");
  if (importBtn.disabled) {
    alert("Please map all required fields before importing");
    return;
  }

  if (
    !confirm(
      `Are you sure you want to import ${window.PharmacyState.importData.totalRows} rows?`
    )
  ) {
    return;
  }

  importBtn.disabled = true;
  importBtn.textContent = "Importing...";

  fetch(processUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken,
    },
    body: `mapping=${encodeURIComponent(
      JSON.stringify(window.PharmacyState.importData.mapping)
    )}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const msg = `Imported ${data.created} new, updated ${data.updated} medicines.`;
        sessionStorage.setItem(
          "toastMessage",
          JSON.stringify({ message: msg, type: "success" })
        );
        closeImportModal();
        window.location.reload();
      } else {
        showToast(
          "Import failed: " + (data.error || "Unknown error"),
          "error"
        );
        importBtn.disabled = false;
        importBtn.textContent = "Import Medicines";
      }
    })
    .catch((error) => {
      console.error("Import error:", error);
      showToast("Error during import", "error");
      importBtn.disabled = false;
      importBtn.textContent = "Import Medicines";
    });
};

// AJAX Form Submission for Add/Edit
document.addEventListener("submit", function (e) {
  if (e.target && e.target.id === "medicineForm") {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = document.getElementById("saveMedicineBtn");
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Saving...";
    }

    fetch(form.action, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.closeMedicineModal();
          // Use message from server or default
          const msg = data.message || "Medicine saved successfully";

          // Determine type based on modal title
          const title = document.getElementById("modalTitle").textContent;
          const isEdit = title.includes("Edit");
          const type = isEdit ? "update" : "success";

          sessionStorage.setItem(
            "toastMessage",
            JSON.stringify({ message: msg, type: type })
          );
          window.location.href = window.location.pathname + "?tab=medicines";
        } else {
          window.showToast("Error: " + JSON.stringify(data.errors), "error");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        window.showToast("An error occurred while saving.", "error");
      })
      .finally(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Save Medicine";
        }
      });
  }
});
