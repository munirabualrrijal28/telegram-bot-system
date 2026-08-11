// User Management JS

let currentUserId = null;
let currentAction = null; // 'freeze' or 'unfreeze'
let config = {};

document.addEventListener('DOMContentLoaded', function() {
    const configDiv = document.getElementById('user-config');
    if (configDiv) {
        config = {
            freezeUrl: configDiv.dataset.userFreezeUrl,
            unfreezeUrl: configDiv.dataset.userUnfreezeUrl,
            detailsUrl: configDiv.dataset.userDetailsUrl
        };
    }
    
    // Bind confirm button
    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', executeAction);
    }
});

// --- View Modal ---

function viewUser(userId) {
    const modal = document.getElementById('viewUserModal');
    const content = document.getElementById('userDetailsContent');
    const url = config.detailsUrl.replace('00000000-0000-0000-0000-000000000000', userId);
    
    // Show modal with loading state
    modal.classList.remove('hidden');
    content.innerHTML = `
        <div class="animate-pulse space-y-3">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
    `;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const u = data.user;
                content.innerHTML = `
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Name</label>
                            <p class="text-sm font-medium text-gray-900">${u.name || '-'}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Email</label>
                            <p class="text-sm font-medium text-gray-900">${u.email || '-'}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Phone</label>
                            <p class="text-sm font-medium text-gray-900">${u.phone || '-'}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Status</label>
                            <span class="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full 
                                ${u.status === 'active' ? 'bg-green-100 text-green-800' : (u.status === 'frozen' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800')}">
                                ${u.status}
                            </span>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Workspace</label>
                            <p class="text-sm font-medium text-gray-900">${u.workspace_name}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Plan</label>
                            <span class="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-50 text-blue-700">
                                ${u.plan_name}
                            </span>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Bots Created</label>
                            <p class="text-sm font-medium text-gray-900">${u.bots_count}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Joined</label>
                            <p class="text-sm font-medium text-gray-900">${u.joined_at}</p>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 uppercase tracking-wide">Free Trial Used</label>
                            <p class="text-sm font-medium text-gray-900">${u.has_used_free_trial ? 'Yes' : 'No'}</p>
                        </div>
                    </div>
                `;
            } else {
                content.innerHTML = `<p class="text-red-600">Error: ${data.error}</p>`;
            }
        })
        .catch(err => {
            content.innerHTML = `<p class="text-red-600">Network error. Please try again.</p>`;
            console.error(err);
        });
}

function closeViewModal() {
    document.getElementById('viewUserModal').classList.add('hidden');
}

// --- Freeze/Unfreeze Logic ---

function confirmFreeze(userId, userName) {
    currentUserId = userId;
    currentAction = 'freeze';
    
    const modal = document.getElementById('confirmModal');
    const title = document.getElementById('confirmTitle');
    const msg = document.getElementById('confirmMessage');
    const icon = document.getElementById('confirmIcon');
    const btn = document.getElementById('confirmBtn');
    
    title.textContent = 'Freeze Account';
    msg.innerHTML = `Are you sure you want to freeze <strong>${userName}</strong>?<br>This will disconnect all their bots and restrict access.`;
    
    icon.className = 'mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10';
    icon.innerHTML = '<svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>';
    
    btn.className = 'w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm';
    btn.textContent = 'Freeze Account';
    
    modal.classList.remove('hidden');
}

function confirmUnfreeze(userId, userName) {
    currentUserId = userId;
    currentAction = 'unfreeze';
    
    const modal = document.getElementById('confirmModal');
    const title = document.getElementById('confirmTitle');
    const msg = document.getElementById('confirmMessage');
    const icon = document.getElementById('confirmIcon');
    const btn = document.getElementById('confirmBtn');
    
    title.textContent = 'Unfreeze Account';
    msg.innerHTML = `Are you sure you want to activate <strong>${userName}</strong>?<br>They will regain access, but must manually reconnect bots.`;
    
    icon.className = 'mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10';
    icon.innerHTML = '<svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
    
    btn.className = 'w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm';
    btn.textContent = 'Activate Account';
    
    modal.classList.remove('hidden');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.add('hidden');
    currentUserId = null;
    currentAction = null;
}

function executeAction() {
    if (!currentUserId || !currentAction) return;
    
    const urlTemplate = currentAction === 'freeze' ? config.freezeUrl : config.unfreezeUrl;
    const url = urlTemplate.replace('00000000-0000-0000-0000-000000000000', currentUserId);
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.cookie.match(/csrftoken=([\w-]+)/)?.[1];
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to reflect changes
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
            closeConfirmModal();
        }
    })
    .catch(err => {
        alert('Network error occurred.');
        console.error(err);
        closeConfirmModal();
    });
}
