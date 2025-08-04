/**
 * Attach Prompt Modal Manager
 * Handles the functionality for attaching prompts to existing prompts
 */
class AttachPromptModalManager {
    constructor() {
        this.modal = null;
        this.currentPromptId = null;
        this.selectedPromptId = null;
        this.searchTimeout = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.modal = document.getElementById('attachPromptModal');
        if (!this.modal) {
            console.error('Attach prompt modal not found');
            return;
        }
        
        this.bindEvents();
        this.setupBootstrapModal();
    }
    
    bindEvents() {
        // Search input events
        const searchInput = document.getElementById('promptSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e.target.value));
            searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
        }
        
        // Clear search button
        const clearBtn = document.getElementById('clearSearchBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearSearch());
        }
        
        // Attach button
        const attachBtn = document.getElementById('attachPromptBtn');
        if (attachBtn) {
            attachBtn.addEventListener('click', () => this.attachPrompt());
        }
        
        // Modal events
        this.modal.addEventListener('show.bs.modal', (e) => this.handleModalShow(e));
        this.modal.addEventListener('hidden.bs.modal', () => this.handleModalHidden());
    }
    
    setupBootstrapModal() {
        // Initialize Bootstrap modal if not already done
        if (typeof bootstrap !== 'undefined' && !this.modal._bsModal) {
            this.bootstrapModal = new bootstrap.Modal(this.modal);
        }
    }
    
    /**
     * Open modal for a specific prompt
     */
    open(promptId) {
        this.currentPromptId = promptId;
        this.selectedPromptId = null;
        
        // Reset modal state
        this.resetModalState();
        
        // Show modal
        if (this.bootstrapModal) {
            this.bootstrapModal.show();
        } else {
            this.modal.classList.add('show');
            this.modal.style.display = 'block';
        }
        
        // Load initial prompts
        this.loadAvailablePrompts();
    }
    
    /**
     * Reset modal to initial state
     */
    resetModalState() {
        // Clear search
        const searchInput = document.getElementById('promptSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Hide all sections
        this.hideSection('searchLoading');
        this.hideSection('searchResults');
        this.hideSection('selectedPromptPreview');
        this.hideSection('searchError');
        
        // Disable attach button
        const attachBtn = document.getElementById('attachPromptBtn');
        if (attachBtn) {
            attachBtn.disabled = true;
        }
        
        // Clear selected prompt
        this.selectedPromptId = null;
    }
    
    /**
     * Handle search input with debouncing
     */
    handleSearchInput(value) {
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Set new timeout for debounced search
        this.searchTimeout = setTimeout(() => {
            this.performSearch(value);
        }, 300);
    }
    
    /**
     * Handle search keydown events
     */
    handleSearchKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.performSearch(e.target.value);
        } else if (e.key === 'Escape') {
            this.clearSearch();
        }
    }
    
    /**
     * Perform search for prompts
     */
    async performSearch(query) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showSection('searchLoading');
        this.hideSection('searchResults');
        this.hideSection('searchError');
        
        try {
            const params = new URLSearchParams();
            if (query && query.trim()) {
                params.append('search', query.trim());
            }
            
            const url = `/api/prompts/${this.currentPromptId}/attached/available?${params}`;
            console.log('🔍 Searching prompts with URL:', url);
            
            const response = await fetch(url);
            console.log('📡 Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Response data:', data);
            
            if (data.success) {
                console.log(`✅ Found ${data.data.length} prompts for attachment`);
                this.displaySearchResults(data.data, query);
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError(`Search failed: ${error.message}`);
        } finally {
            this.isLoading = false;
            this.hideSection('searchLoading');
        }
    }
    
    /**
     * Display search results
     */
    displaySearchResults(prompts, query) {
        const resultsContainer = document.getElementById('searchResults');
        const promptsList = document.getElementById('promptsList');
        const noResults = document.getElementById('noResults');
        
        if (!resultsContainer || !promptsList || !noResults) return;
        
        // Clear previous results
        promptsList.innerHTML = '';
        
        // Add diagnostic information
        const diagnosticInfo = document.createElement('div');
        diagnosticInfo.className = 'alert alert-info mb-3';
        diagnosticInfo.innerHTML = `
            <strong>🔍 Diagnostic Information:</strong><br>
            • Total prompts found: <strong>${prompts.length}</strong><br>
            • Search query: <strong>"${query || 'none'}"</strong><br>
            • Current prompt ID: <strong>${this.currentPromptId}</strong><br>
            • API endpoint: <strong>/api/prompts/${this.currentPromptId}/attached/available</strong>
        `;
        promptsList.appendChild(diagnosticInfo);
        
        if (prompts.length === 0) {
            this.showSection('noResults');
            this.hideSection('searchResults');
            return;
        }
        
        this.hideSection('noResults');
        this.showSection('searchResults');
        
        // Create prompt items
        prompts.forEach(prompt => {
            const promptItem = this.createPromptItem(prompt, query);
            promptsList.appendChild(promptItem);
        });
    }
    
    /**
     * Create a prompt item element
     */
    createPromptItem(prompt, query) {
        const template = document.getElementById('promptItemTemplate');
        if (!template) {
            return this.createPromptItemFallback(prompt, query);
        }
        
        const clone = template.content.cloneNode(true);
        const item = clone.querySelector('.prompt-item');
        
        // Set data attributes
        item.setAttribute('data-prompt-id', prompt.id);
        
        // Set content
        const title = item.querySelector('.prompt-title');
        const content = item.querySelector('.prompt-content');
        const tags = item.querySelector('.prompt-tags');
        
        if (title) {
            title.textContent = this.highlightSearch(prompt.title, query);
        }
        
        if (content) {
            const preview = prompt.content.length > 100 
                ? prompt.content.substring(0, 100) + '...' 
                : prompt.content;
            content.textContent = this.highlightSearch(preview, query);
        }
        
        if (tags && prompt.tags) {
            tags.innerHTML = prompt.tags.map(tag => 
                `<span class="badge bg-secondary me-1" style="background-color: ${tag.color || '#6c757d'} !important;">${tag.name}</span>`
            ).join('');
        }
        
        // Bind select button
        const selectBtn = item.querySelector('.select-prompt-btn');
        if (selectBtn) {
            selectBtn.addEventListener('click', (e) => {
                console.log('🔘 Select button clicked for prompt:', prompt.id);
                e.preventDefault();
                e.stopPropagation();
                this.selectPrompt(prompt);
            });
            
            // Add visual feedback for debugging
            selectBtn.style.border = '2px solid red';
            selectBtn.style.backgroundColor = 'yellow';
            selectBtn.style.color = 'black';
            selectBtn.innerHTML = '<i class="bi bi-plus-circle me-1"></i>CLICK ME!';
        }
        
        return item;
    }
    
    /**
     * Fallback method for creating prompt items without template
     */
    createPromptItemFallback(prompt, query) {
        const item = document.createElement('div');
        item.className = 'list-group-item list-group-item-action prompt-item';
        item.setAttribute('data-prompt-id', prompt.id);
        
        item.innerHTML = `
            <div class="d-flex w-100 justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1 prompt-title">${this.highlightSearch(prompt.title, query)}</h6>
                    <p class="mb-1 prompt-content text-muted small">${this.highlightSearch(prompt.content.substring(0, 100) + (prompt.content.length > 100 ? '...' : ''), query)}</p>
                    <div class="prompt-tags">
                        ${prompt.tags ? prompt.tags.map(tag => 
                            `<span class="badge bg-secondary me-1" style="background-color: ${tag.color || '#6c757d'} !important;">${tag.name}</span>`
                        ).join('') : ''}
                    </div>
                </div>
                <div class="ms-3">
                    <button class="btn btn-sm btn-outline-primary select-prompt-btn">
                        <i class="bi bi-plus-circle me-1"></i>Select
                    </button>
                </div>
            </div>
        `;
        
        // Bind select button
        const selectBtn = item.querySelector('.select-prompt-btn');
        selectBtn.addEventListener('click', (e) => {
            console.log('🔘 Select button clicked (fallback) for prompt:', prompt.id);
            e.preventDefault();
            e.stopPropagation();
            this.selectPrompt(prompt);
        });
        
        // Add visual feedback for debugging
        selectBtn.style.border = '2px solid red';
        selectBtn.style.backgroundColor = 'yellow';
        selectBtn.style.color = 'black';
        selectBtn.innerHTML = '<i class="bi bi-plus-circle me-1"></i>CLICK ME!';
        
        return item;
    }
    
    /**
     * Highlight search terms in text
     */
    highlightSearch(text, query) {
        if (!query || !query.trim()) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }
    
    /**
     * Select a prompt for attachment
     */
    selectPrompt(prompt) {
        console.log('🎯 Selecting prompt:', prompt.id, prompt.title);
        this.selectedPromptId = prompt.id;
        this.showPromptPreview(prompt);
        
        // Enable attach button
        const attachBtn = document.getElementById('attachPromptBtn');
        if (attachBtn) {
            attachBtn.disabled = false;
            console.log('✅ Attach button enabled');
        }
        
        // Update UI to show selection
        this.updateSelectionUI(prompt.id);
        
        // Show success message
        this.showSuccess(`Selected: ${prompt.title}`);
    }
    
    /**
     * Show prompt preview
     */
    showPromptPreview(prompt) {
        const previewContainer = document.getElementById('selectedPromptPreview');
        const title = document.getElementById('selectedPromptTitle');
        const content = document.getElementById('selectedPromptContent');
        const tags = document.getElementById('selectedPromptTags');
        
        if (!previewContainer || !title || !content || !tags) return;
        
        title.textContent = prompt.title;
        content.textContent = prompt.content.length > 200 
            ? prompt.content.substring(0, 200) + '...' 
            : prompt.content;
        
        tags.innerHTML = prompt.tags ? prompt.tags.map(tag => 
            `<span class="badge bg-secondary me-1" style="background-color: ${tag.color || '#6c757d'} !important;">${tag.name}</span>`
        ).join('') : '';
        
        this.showSection('selectedPromptPreview');
    }
    
    /**
     * Update UI to show which prompt is selected
     */
    updateSelectionUI(selectedId) {
        // Remove previous selections
        document.querySelectorAll('.prompt-item').forEach(item => {
            item.classList.remove('active');
            const btn = item.querySelector('.select-prompt-btn');
            if (btn) {
                btn.innerHTML = '<i class="bi bi-plus-circle me-1"></i>Select';
                btn.className = 'btn btn-sm btn-outline-primary select-prompt-btn';
            }
        });
        
        // Highlight selected item
        const selectedItem = document.querySelector(`[data-prompt-id="${selectedId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
            const btn = selectedItem.querySelector('.select-prompt-btn');
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Selected';
                btn.className = 'btn btn-sm btn-success select-prompt-btn';
            }
        }
    }
    
    /**
     * Attach the selected prompt
     */
    async attachPrompt() {
        if (!this.selectedPromptId) {
            this.showError('No prompt selected');
            return;
        }
        
        const attachBtn = document.getElementById('attachPromptBtn');
        if (attachBtn) {
            attachBtn.disabled = true;
            attachBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Attaching...';
        }
        
        try {
            const response = await fetch(`/api/prompts/${this.currentPromptId}/attach`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attached_prompt_id: this.selectedPromptId
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Prompt attached successfully!');
                this.close();
                
                // Refresh the page to show updated attached prompts
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Failed to attach prompt');
            }
            
        } catch (error) {
            console.error('Attach error:', error);
            this.showError(`Failed to attach prompt: ${error.message}`);
            
            // Re-enable button
            if (attachBtn) {
                attachBtn.disabled = false;
                attachBtn.innerHTML = '<i class="bi bi-link-45deg me-1"></i>Attach Prompt';
            }
        }
    }
    
    /**
     * Load available prompts for attachment
     */
    async loadAvailablePrompts() {
        await this.performSearch('');
    }
    
    /**
     * Clear search
     */
    clearSearch() {
        const searchInput = document.getElementById('promptSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = null;
        }
        
        this.loadAvailablePrompts();
    }
    
    /**
     * Close modal
     */
    close() {
        if (this.bootstrapModal) {
            this.bootstrapModal.hide();
        } else {
            this.modal.classList.remove('show');
            this.modal.style.display = 'none';
        }
    }
    
    /**
     * Handle modal show event
     */
    handleModalShow(e) {
        // Focus search input
        setTimeout(() => {
            const searchInput = document.getElementById('promptSearchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }, 100);
    }
    
    /**
     * Handle modal hidden event
     */
    handleModalHidden() {
        this.resetModalState();
        this.currentPromptId = null;
        this.selectedPromptId = null;
    }
    
    /**
     * Show a section
     */
    showSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'block';
        }
    }
    
    /**
     * Hide a section
     */
    hideSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'none';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        const errorContainer = document.getElementById('searchError');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorContainer && errorMessage) {
            errorMessage.textContent = message;
            this.showSection('searchError');
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        // Create toast notification
        this.createToast('success', message);
    }
    
    /**
     * Create toast notification
     */
    createToast(type, message) {
        const toastContainer = document.getElementById('toastContainer') || document.body;
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback for when Bootstrap is not available
            toast.style.display = 'block';
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
    }
}

// Initialize the modal manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.attachPromptModalManager = new AttachPromptModalManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AttachPromptModalManager;
} 