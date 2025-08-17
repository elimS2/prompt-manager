// Main JavaScript for Prompt Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Auto-hide alerts
    autoHideAlerts();

    // Initialize auth controls
    initializeAuthControls();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form enhancements
function initializeFormEnhancements() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Character counters
    const charCountElements = document.querySelectorAll('[data-char-count]');
    charCountElements.forEach(element => {
        const targetId = element.getAttribute('data-char-count');
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.addEventListener('input', function() {
                element.textContent = this.value.length;
            });
        }
    });
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new prompt
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            window.location.href = '/prompts/create';
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// Auto-hide alerts after 5 seconds
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Enhanced copy to clipboard with better feedback
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(function() {
        // Visual feedback
        if (buttonElement) {
            const originalText = buttonElement.innerHTML;
            buttonElement.innerHTML = '<i class="bi bi-check"></i> Copied!';
            buttonElement.classList.add('btn-success');
            
            setTimeout(() => {
                buttonElement.innerHTML = originalText;
                buttonElement.classList.remove('btn-success');
            }, 2000);
        } else {
            showToast('Copied to clipboard!', 'success');
        }
    }, function(err) {
        console.error('Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Confirm before destructive actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

// Loading state management
function setLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.setAttribute('disabled', 'disabled');
        
        // Add spinner if button
        if (element.tagName === 'BUTTON') {
            element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + element.innerHTML;
        }
    } else {
        element.classList.remove('loading');
        element.removeAttribute('disabled');
        
        // Remove spinner
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in templates
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
window.confirmAction = confirmAction;
window.setLoading = setLoading;
window.debounce = debounce;

// Ensure Bootstrap modals are appended to <body> to avoid being trapped under overlays/stacking contexts
document.addEventListener('DOMContentLoaded', () => {
    try {
        document.querySelectorAll('.modal').forEach(modalEl => {
            if (modalEl && modalEl.parentElement !== document.body) {
                document.body.appendChild(modalEl);
            }
        });
    } catch (e) {
        // noop
    }
});

// Initialize auth controls (Google login loading feedback)
function initializeAuthControls() {
    const loginLinks = document.querySelectorAll('[data-google-login]');
    loginLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            if (link.classList.contains('disabled')) {
                return;
            }
            e.preventDefault();
            link.classList.add('disabled');
            link.setAttribute('aria-disabled', 'true');
            link.setAttribute('aria-busy', 'true');
            setLoading(link, true);
            // Allow the spinner to render before navigating
            setTimeout(() => {
                window.location.href = link.getAttribute('href');
            }, 75);
        });
    });
}