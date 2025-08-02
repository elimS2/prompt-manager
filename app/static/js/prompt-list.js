/**
 * Prompt List JavaScript Module
 * Handles all interactive functionality for the prompts list page
 */

class PromptListManager {
    constructor() {
        this.mergeBtn = document.getElementById('mergeBtn');
        this.checkboxes = document.querySelectorAll('.prompt-checkbox');
        this.toggleButtons = document.querySelectorAll('.toggle-content-btn');
        this.copyButtons = document.querySelectorAll('.copy-content-btn');
        this.filterInputs = document.querySelectorAll('input[name="is_active"]');
        this.archiveForms = document.querySelectorAll('.archive-form');
        this.restoreForms = document.querySelectorAll('.restore-form');
        
        this.init();
    }
    
    init() {
        this.initCheckboxes();
        this.initToggleButtons();
        this.initCopyButtons();
        this.initFilterInputs();
        this.initArchiveForms();
        this.initRestoreForms();
        this.initKeyboardShortcuts();
    }
    
    /**
     * Initialize checkbox functionality for merge selection and copy on click
     */
    initCheckboxes() {
        this.checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateMergeButton());
            checkbox.addEventListener('click', (e) => this.handleCheckboxClick(e));
        });
    }
    
    /**
     * Update merge button state based on selected prompts
     */
    updateMergeButton() {
        const checkedBoxes = document.querySelectorAll('.prompt-checkbox:checked');
        this.mergeBtn.disabled = checkedBoxes.length < 2;
        
        if (checkedBoxes.length >= 2) {
            this.mergeBtn.onclick = () => {
                const ids = Array.from(checkedBoxes).map(cb => cb.value);
                const mergeUrl = this.mergeBtn.getAttribute('data-merge-url') || '/prompts/merge';
                window.location.href = `${mergeUrl}?ids=${ids.join('&ids=')}`;
            };
        }
    }
    
    /**
     * Handle checkbox click to copy prompt content
     */
    handleCheckboxClick(event) {
        const checkbox = event.currentTarget;
        const card = checkbox.closest('.prompt-card');
        const copyButton = card.querySelector('.copy-content-btn');
        
        if (copyButton) {
            const content = copyButton.getAttribute('data-content');
            if (content) {
                // Small delay to ensure checkbox state changes first
                setTimeout(() => {
                    this.copyToClipboard(content, copyButton);
                }, 50);
            }
        }
    }
    
    /**
     * Initialize content toggle buttons
     */
    initToggleButtons() {
        this.toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleContentToggle(e));
        });
    }
    
    /**
     * Handle content toggle functionality
     */
    handleContentToggle(event) {
        const button = event.currentTarget;
        const card = button.closest('.prompt-card');
        const contentPreview = card.querySelector('.content-preview');
        const icon = button.querySelector('i');
        
        if (contentPreview.style.display === 'none') {
            this.showContent(contentPreview, icon, button);
        } else {
            this.hideContent(contentPreview, icon, button);
        }
        
        // Reinitialize tooltip
        this.reinitializeTooltip(button);
    }
    
    /**
     * Show content preview with animation
     */
    showContent(contentPreview, icon, button) {
        contentPreview.style.display = 'block';
        contentPreview.classList.add('slide-down');
        icon.className = 'bi bi-chevron-up';
        button.setAttribute('title', 'Hide content');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            contentPreview.classList.remove('slide-down');
        }, 300);
    }
    
    /**
     * Hide content preview with animation
     */
    hideContent(contentPreview, icon, button) {
        contentPreview.classList.add('slide-up');
        icon.className = 'bi bi-chevron-down';
        button.setAttribute('title', 'Show content');
        
        // Hide element after animation completes
        setTimeout(() => {
            contentPreview.style.display = 'none';
            contentPreview.classList.remove('slide-up');
        }, 300);
    }
    
    /**
     * Initialize copy content buttons
     */
    initCopyButtons() {
        this.copyButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleCopyContent(e));
        });
    }
    
    /**
     * Handle copy content functionality
     */
    handleCopyContent(event) {
        const button = event.currentTarget;
        const content = button.getAttribute('data-content');
        
        if (content) {
            this.copyToClipboard(content, button);
        }
    }
    
    /**
     * Enhanced copy to clipboard with visual feedback
     */
    copyToClipboard(text, buttonElement) {
        navigator.clipboard.writeText(text).then(() => {
            this.showCopySuccess(buttonElement);
            this.showToast('Content copied to clipboard!', 'success');
        }).catch((err) => {
            console.error('Could not copy text: ', err);
            this.showToast('Failed to copy to clipboard', 'error');
        });
    }
    
    /**
     * Show copy success visual feedback
     */
    showCopySuccess(buttonElement) {
        const originalHTML = buttonElement.innerHTML;
        const originalClass = buttonElement.className;
        
        buttonElement.innerHTML = '<i class="bi bi-check"></i>';
        buttonElement.className = originalClass.replace('btn-outline-primary', 'btn-success');
        
        setTimeout(() => {
            buttonElement.innerHTML = originalHTML;
            buttonElement.className = originalClass;
        }, 2000);
    }
    
    /**
     * Initialize filter inputs
     */
    initFilterInputs() {
        this.filterInputs.forEach(input => {
            input.addEventListener('change', (e) => this.handleFilterChange(e));
        });
    }
    
    /**
     * Initialize archive forms with enhanced UX
     */
    initArchiveForms() {
        this.archiveForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleArchiveSubmit(e));
        });
    }
    
    /**
     * Handle archive form submission with confirmation and feedback
     */
    handleArchiveSubmit(event) {
        event.preventDefault();
        
        const form = event.currentTarget;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.innerHTML;
        const promptTitle = form.closest('.prompt-card').querySelector('.card-title').textContent.trim();
        
        // Show confirmation dialog
        if (!confirm(`Are you sure you want to archive "${promptTitle}"?`)) {
            return;
        }
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        button.setAttribute('title', 'Archiving...');
        
        // Submit form
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new FormData(form)
        })
        .then(response => {
            if (response.ok) {
                // Show success feedback
                this.showToast('Prompt archived successfully!', 'success');
                
                // Remove the card with animation
                const card = form.closest('.prompt-card');
                card.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                card.style.opacity = '0';
                card.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    card.remove();
                    
                    // Check if no cards left
                    const remainingCards = document.querySelectorAll('.prompt-card');
                    if (remainingCards.length === 0) {
                        this.showEmptyState();
                    }
                }, 300);
            } else {
                throw new Error('Failed to archive prompt');
            }
        })
        .catch(error => {
            console.error('Archive error:', error);
            this.showToast('Failed to archive prompt. Please try again.', 'error');
            
            // Restore button state
            button.disabled = false;
            button.innerHTML = originalText;
            button.setAttribute('title', 'Archive prompt');
        });
    }
    
    /**
     * Show empty state when all prompts are archived
     */
    showEmptyState() {
        const promptsList = document.getElementById('promptsList');
        promptsList.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="bi bi-archive display-1 text-muted"></i>
                    <h3 class="text-muted mt-3">All prompts archived</h3>
                    <p class="text-muted">No active prompts found.</p>
                    <a href="{{ url_for('prompt.create') }}" class="btn btn-primary">
                        <i class="bi bi-plus-circle me-2"></i>Create New Prompt
                    </a>
                </div>
            </div>
        `;
    }
    
    /**
     * Initialize restore forms with enhanced UX
     */
    initRestoreForms() {
        this.restoreForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleRestoreSubmit(e));
        });
    }
    
    /**
     * Handle restore form submission with confirmation and feedback
     */
    handleRestoreSubmit(event) {
        event.preventDefault();
        
        const form = event.currentTarget;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.innerHTML;
        const promptTitle = form.closest('.prompt-card').querySelector('.card-title').textContent.trim();
        
        // Show confirmation dialog
        if (!confirm(`Are you sure you want to restore "${promptTitle}"?`)) {
            return;
        }
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        button.setAttribute('title', 'Restoring...');
        
        // Submit form
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new FormData(form)
        })
        .then(response => {
            if (response.ok) {
                // Show success feedback
                this.showToast('Prompt restored successfully!', 'success');
                
                // Remove the card with animation
                const card = form.closest('.prompt-card');
                card.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                
                setTimeout(() => {
                    card.remove();
                    
                    // Check if no cards left
                    const remainingCards = document.querySelectorAll('.prompt-card');
                    if (remainingCards.length === 0) {
                        this.showEmptyState();
                    }
                }, 300);
            } else {
                throw new Error('Failed to restore prompt');
            }
        })
        .catch(error => {
            console.error('Restore error:', error);
            this.showToast('Failed to restore prompt. Please try again.', 'error');
            
            // Restore button state
            button.disabled = false;
            button.innerHTML = originalText;
            button.setAttribute('title', 'Restore prompt');
        });
    }
    
    /**
     * Handle filter changes
     */
    handleFilterChange(event) {
        const input = event.currentTarget;
        const url = new URL(window.location);
        
        if (input.value) {
            url.searchParams.set('is_active', input.value);
        } else {
            url.searchParams.delete('is_active');
        }
        
        window.location.href = url.toString();
    }
    
    /**
     * Initialize keyboard shortcuts
     */
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K for search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new prompt
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            const createUrl = document.querySelector('a[href*="/create"]')?.href || '/prompts/create';
            window.location.href = createUrl;
        }
        
        // Escape to close any open content previews
        if (event.key === 'Escape') {
            this.closeAllContentPreviews();
        }
    }
    
    /**
     * Close all open content previews
     */
    closeAllContentPreviews() {
        const openPreviews = document.querySelectorAll('.content-preview[style*="display: block"]');
        openPreviews.forEach(preview => {
            const card = preview.closest('.prompt-card');
            const button = card.querySelector('.toggle-content-btn');
            const icon = button.querySelector('i');
            
            this.hideContent(preview, icon, button);
        });
    }
    
    /**
     * Reinitialize Bootstrap tooltip
     */
    reinitializeTooltip(element) {
        const tooltip = bootstrap.Tooltip.getInstance(element);
        if (tooltip) {
            tooltip.dispose();
        }
        new bootstrap.Tooltip(element);
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            // Fallback toast implementation
            this.createToast(message, type);
        }
    }
    
    /**
     * Create fallback toast notification
     */
    createToast(message, type) {
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the prompts list page
    if (document.querySelector('.prompt-card')) {
        new PromptListManager();
    }
});

// Export for potential use in other modules
window.PromptListManager = PromptListManager; 