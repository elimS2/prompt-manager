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
        
        // New properties for multi-select functionality
        this.selectedPrompts = new Set();
        this.copyAllBtn = null;
        
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
        this.createActionButtons();
    }
    
    /**
     * Create action buttons for multi-select functionality
     */
    createActionButtons() {
        const actionsBar = document.querySelector('.d-flex.justify-content-between.align-items-center');
        if (actionsBar) {
            const actionsDiv = actionsBar.querySelector('div');
            if (actionsDiv) {
                // Create "Copy All Selected" button
                this.copyAllBtn = document.createElement('button');
                this.copyAllBtn.className = 'btn btn-info me-2';
                this.copyAllBtn.id = 'copyAllBtn';
                this.copyAllBtn.disabled = true;
                this.copyAllBtn.innerHTML = '<i class="bi bi-clipboard-plus me-1"></i>Copy Selected';
                this.copyAllBtn.setAttribute('data-bs-toggle', 'tooltip');
                this.copyAllBtn.setAttribute('title', 'Copy content of all selected prompts');
                
                this.copyAllBtn.addEventListener('click', () => this.copyAllSelectedPrompts());
                
                // Create "Clear Selection" button
                this.clearSelectionBtn = document.createElement('button');
                this.clearSelectionBtn.className = 'btn btn-outline-secondary me-2';
                this.clearSelectionBtn.id = 'clearSelectionBtn';
                this.clearSelectionBtn.disabled = true;
                this.clearSelectionBtn.innerHTML = '<i class="bi bi-x-circle me-1"></i>Clear Selection';
                this.clearSelectionBtn.setAttribute('data-bs-toggle', 'tooltip');
                this.clearSelectionBtn.setAttribute('title', 'Clear selection and clipboard');
                
                this.clearSelectionBtn.addEventListener('click', () => this.clearSelectionAndClipboard());
                
                // Insert buttons before the merge button
                const mergeBtn = actionsDiv.querySelector('#mergeBtn');
                if (mergeBtn) {
                    actionsDiv.insertBefore(this.clearSelectionBtn, mergeBtn);
                    actionsDiv.insertBefore(this.copyAllBtn, this.clearSelectionBtn);
                } else {
                    actionsDiv.appendChild(this.copyAllBtn);
                    actionsDiv.appendChild(this.clearSelectionBtn);
                }
                
                // Initialize tooltips
                new bootstrap.Tooltip(this.copyAllBtn);
                new bootstrap.Tooltip(this.clearSelectionBtn);
            }
        }
    }
    
    /**
     * Initialize checkbox functionality for merge selection and multi-copy
     */
    initCheckboxes() {
        this.checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.handleCheckboxChange(checkbox));
            checkbox.addEventListener('click', (e) => this.handleCheckboxClick(e));
        });
    }
    
    /**
     * Handle checkbox change event
     */
    handleCheckboxChange(checkbox) {
        const promptId = checkbox.value;
        const card = checkbox.closest('.prompt-card');
        
        if (checkbox.checked) {
            this.selectedPrompts.add(promptId);
            card.classList.add('selected');
        } else {
            this.selectedPrompts.delete(promptId);
            card.classList.remove('selected');
        }
        
        this.updateUI();
    }
    
    /**
     * Update UI based on selected prompts
     */
    updateUI() {
        const selectedCount = this.selectedPrompts.size;
        
        // Update merge button
        this.mergeBtn.disabled = selectedCount < 2;
        
        // Update copy all button
        if (this.copyAllBtn) {
            this.copyAllBtn.disabled = selectedCount === 0;
            this.copyAllBtn.innerHTML = `<i class="bi bi-clipboard-plus me-1"></i>Copy Selected (${selectedCount})`;
            
            // Update tooltip
            const tooltip = bootstrap.Tooltip.getInstance(this.copyAllBtn);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(this.copyAllBtn, {
                title: selectedCount === 0 
                    ? 'Select prompts to copy' 
                    : `Copy content of ${selectedCount} selected prompt${selectedCount > 1 ? 's' : ''}`
            });
        }
        
        // Update clear selection button
        if (this.clearSelectionBtn) {
            this.clearSelectionBtn.disabled = selectedCount === 0;
            
            // Update tooltip
            const tooltip = bootstrap.Tooltip.getInstance(this.clearSelectionBtn);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(this.clearSelectionBtn, {
                title: selectedCount === 0 
                    ? 'No selection to clear' 
                    : `Clear ${selectedCount} selected prompt${selectedCount > 1 ? 's' : ''} and clipboard`
            });
        }
        
        // Update merge button functionality
        if (selectedCount >= 2) {
            this.mergeBtn.onclick = () => {
                const ids = Array.from(this.selectedPrompts);
                const mergeUrl = this.mergeBtn.getAttribute('data-merge-url') || '/prompts/merge';
                window.location.href = `${mergeUrl}?ids=${ids.join('&ids=')}`;
            };
        }
        
        // Update checkbox tooltips
        this.updateCheckboxTooltips();
    }
    
    /**
     * Update checkbox tooltips based on selection state
     */
    updateCheckboxTooltips() {
        this.checkboxes.forEach(checkbox => {
            const tooltip = bootstrap.Tooltip.getInstance(checkbox);
            if (tooltip) {
                tooltip.dispose();
            }
            
            const selectedCount = this.selectedPrompts.size;
            let tooltipText = '';
            
            if (checkbox.checked) {
                if (selectedCount === 1) {
                    tooltipText = 'Click to copy this prompt content';
                } else {
                    tooltipText = `Click to copy content of ${selectedCount} selected prompts`;
                }
            } else {
                tooltipText = 'Click to select and copy this prompt content';
            }
            
            new bootstrap.Tooltip(checkbox, { title: tooltipText });
        });
    }
    
    /**
     * Handle checkbox click to copy selected prompts content
     */
    handleCheckboxClick(event) {
        // Small delay to ensure checkbox state changes first
        setTimeout(() => {
            if (this.selectedPrompts.size > 0) {
                this.copyAllSelectedPrompts();
            }
        }, 100);
    }
    
    /**
     * Copy content of all selected prompts
     */
    copyAllSelectedPrompts() {
        const selectedContents = [];
        
        this.selectedPrompts.forEach(promptId => {
            const checkbox = document.querySelector(`#prompt-${promptId}`);
            if (checkbox) {
                const card = checkbox.closest('.prompt-card');
                const copyButton = card.querySelector('.copy-content-btn');
                const title = card.querySelector('.card-title').textContent.trim();
                
                if (copyButton) {
                    const content = copyButton.getAttribute('data-content');
                    if (content) {
                        selectedContents.push({
                            title: title,
                            content: content
                        });
                    }
                }
            }
        });
        
        if (selectedContents.length > 0) {
            const combinedContent = this.formatCombinedContent(selectedContents);
            this.copyToClipboard(combinedContent, this.copyAllBtn);
            
            // Show visual feedback on all selected cards
            this.showMultiCopySuccess();
            
            // Show success message
            const count = selectedContents.length;
            const message = count === 1 
                ? 'Prompt content copied to clipboard!' 
                : `Content of ${count} prompts copied to clipboard!`;
            this.showToast(message, 'success');
        }
    }
    
    /**
     * Format combined content from multiple prompts
     */
    formatCombinedContent(selectedContents) {
        if (selectedContents.length === 1) {
            return selectedContents[0].content;
        }
        
        let combined = '';
        selectedContents.forEach((item, index) => {
            combined += `=== ${item.title} ===\n\n`;
            combined += item.content;
            
            if (index < selectedContents.length - 1) {
                combined += '\n\n' + '='.repeat(50) + '\n\n';
            }
        });
        
        return combined;
    }
    
    /**
     * Show visual feedback for multi-copy operation
     */
    showMultiCopySuccess() {
        this.selectedPrompts.forEach(promptId => {
            const checkbox = document.querySelector(`#prompt-${promptId}`);
            if (checkbox) {
                const card = checkbox.closest('.prompt-card');
                
                // Add success styling using CSS class
                card.classList.add('copy-success');
                
                // Remove styling after animation
                setTimeout(() => {
                    card.classList.remove('copy-success');
                }, 2000);
            }
        });
    }
    
    /**
     * Clear selection and clipboard
     */
    clearSelectionAndClipboard() {
        const selectedCount = this.selectedPrompts.size;
        
        if (selectedCount === 0) {
            this.showToast('No selection to clear', 'info');
            return;
        }
        
        // Clear clipboard by writing empty string
        navigator.clipboard.writeText('').then(() => {
            // Clear all checkboxes
            this.checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    checkbox.checked = false;
                    this.handleCheckboxChange(checkbox);
                }
            });
            
            // Show visual feedback
            this.showClearSelectionSuccess();
            
            // Show success message
            const message = selectedCount === 1 
                ? 'Selection cleared and clipboard emptied!' 
                : `${selectedCount} selections cleared and clipboard emptied!`;
            this.showToast(message, 'success');
            
        }).catch((err) => {
            console.error('Could not clear clipboard: ', err);
            this.showToast('Failed to clear clipboard', 'error');
        });
    }
    
    /**
     * Show visual feedback for clear selection operation
     */
    showClearSelectionSuccess() {
        // Add visual feedback to the clear button
        const originalHTML = this.clearSelectionBtn.innerHTML;
        const originalClass = this.clearSelectionBtn.className;
        
        this.clearSelectionBtn.innerHTML = '<i class="bi bi-check"></i>';
        this.clearSelectionBtn.className = originalClass.replace('btn-outline-secondary', 'btn-success');
        
        setTimeout(() => {
            this.clearSelectionBtn.innerHTML = originalHTML;
            this.clearSelectionBtn.className = originalClass;
        }, 2000);
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
        
        // Handle different button types
        let successClass = '';
        if (originalClass.includes('btn-outline-primary')) {
            successClass = originalClass.replace('btn-outline-primary', 'btn-success');
        } else if (originalClass.includes('btn-info')) {
            successClass = originalClass.replace('btn-info', 'btn-success');
        } else {
            successClass = originalClass;
        }
        
        buttonElement.innerHTML = '<i class="bi bi-check"></i>';
        buttonElement.className = successClass;
        
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
        
        // Ctrl/Cmd + C for copy selected prompts
        if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
            event.preventDefault();
            if (this.selectedPrompts.size > 0) {
                this.copyAllSelectedPrompts();
            }
        }
        
        // Ctrl/Cmd + A for select all prompts
        if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
            event.preventDefault();
            this.selectAllPrompts();
        }
        
        // Ctrl/Cmd + Shift + C for clear selection and clipboard
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
            event.preventDefault();
            this.clearSelectionAndClipboard();
        }
        
        // Escape to close any open content previews
        if (event.key === 'Escape') {
            this.closeAllContentPreviews();
        }
    }
    
    /**
     * Select all prompts
     */
    selectAllPrompts() {
        this.checkboxes.forEach(checkbox => {
            if (!checkbox.checked) {
                checkbox.checked = true;
                this.handleCheckboxChange(checkbox);
            }
        });
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