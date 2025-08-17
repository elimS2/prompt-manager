/**
 * Prompt List JavaScript Module
 * Handles all interactive functionality for the prompts list page
 */

console.log('🚀 PromptListManager script loaded!');

class PromptListManager {
    constructor() {
        console.log('🔧 PromptListManager constructor called');
        
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
        
        // Properties for attach mode
        this.attachMode = false;
        this.mainPromptId = null;
        
        // Combination tracking
        this.lastSelectionTime = null;
        this.lastSelectedPromptId = null;
        this.combinationSelectionTimeout = null;
        
        // Combined content panel elements
        this.combinedContentPanel = document.getElementById('combinedContentPanel');
        this.combinedContentTextarea = document.getElementById('combinedContentTextarea');
        this.selectedCountBadge = document.getElementById('selectedCount');
        this.copyCombinedBtn = document.getElementById('copyCombinedBtn');
        this.clearCombinedBtn = document.getElementById('clearCombinedBtn');
        this.charCountSpan = document.getElementById('charCount');
        this.wordCountSpan = document.getElementById('wordCount');
        
        // Panel toggle functionality
        this.toggleCombinedPanelBtn = document.getElementById('toggleCombinedPanelBtn');
        this.isPanelVisible = false;
        this.panelVisibilityPreference = localStorage.getItem('combinedPanelVisible') === 'true';
        
        // Favorites UI
        this.saveFavoriteBtn = document.getElementById('saveFavoriteBtn');
        this.favoritesDropdownMenu = document.getElementById('favoritesDropdownMenu');
        this.mergeFavoriteToggle = document.getElementById('mergeFavoriteToggle');
        this.saveFavoriteModal = null;
        this.favoriteNameInput = null;
        this.favoriteSelectionInfo = null;
        this.confirmSaveFavoriteBtn = null;
        this.favorites = [];

        // Programmatic selection guard to prevent unintended pair-copy behavior
        this.suppressCombinationCopy = false;
        
        // Tag filtering functionality
        this.tagFiltersContainer = document.querySelector('.popular-tags-container');
        this.currentStatusFilter = this.getCurrentStatusFilter();
        
        this.init();
    }
    
    init() {
        console.log('🚀 PromptListManager init() called');
        this.initCheckboxes();
        this.initToggleButtons();
        this.initCopyButtons();
        this.initFilterInputs();
        this.initArchiveForms();
        this.initRestoreForms();
        this.initKeyboardShortcuts();
        this.createActionButtons();
        this.initCombinedContentPanel();
        this.initPanelToggleButton();
        this.restorePanelVisibility();
        this.initFavorites();
        this.initTagFilters();
        this.syncSelectedTagVisualsWithURL();
        this.initStatusFilterListener();
        this.initDragAndDrop();
        this.initAttachedPrompts();
        this.initAttachPromptButtons();
        this.applyFavoriteFromSSR();
        console.log('✅ PromptListManager initialization complete');
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
            
            // Check if this is part of a combination selection
            const now = Date.now();
            if (!this.suppressCombinationCopy && this.lastSelectionTime && (now - this.lastSelectionTime) < 100) {
                // This is likely a combination selection
                const previousPromptId = this.lastSelectedPromptId;
                if (previousPromptId && previousPromptId !== promptId) {
                    // Handle combination copy using existing logic
                    this.handleCombinationCopy(previousPromptId, promptId);
                    
                    // Clear tracking
                    this.lastSelectionTime = null;
                    this.lastSelectedPromptId = null;
                    if (this.combinationSelectionTimeout) {
                        clearTimeout(this.combinationSelectionTimeout);
                        this.combinationSelectionTimeout = null;
                    }
                    return;
                }
            }
            
            // Update tracking for potential combination
            this.lastSelectionTime = now;
            this.lastSelectedPromptId = promptId;
            
            // Clear previous timeout
            if (this.combinationSelectionTimeout) {
                clearTimeout(this.combinationSelectionTimeout);
            }
            
            // Set timeout to clear tracking if no combination occurs
            this.combinationSelectionTimeout = setTimeout(() => {
                this.lastSelectionTime = null;
                this.lastSelectedPromptId = null;
            }, 100);
            
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
        
        // Update Save Favorite button
        if (this.saveFavoriteBtn) {
            this.saveFavoriteBtn.disabled = selectedCount === 0;
        }
        
        // Update merge button functionality
        if (selectedCount >= 2) {
            this.mergeBtn.onclick = () => {
                const ids = Array.from(this.selectedPrompts);
                const mergeUrl = this.mergeBtn.getAttribute('data-merge-url') || '/prompts/merge';
                window.location.href = `${mergeUrl}?ids=${ids.join('&ids=')}`;
            };
        }
        
        // Update combined content panel
        this.updateCombinedContentPanel();
        
        // Update checkbox tooltips
        this.updateCheckboxTooltips();
    }
    
    /**
     * Favorites: init, load, render, save, apply, delete
     */
    initFavorites() {
        if (this.saveFavoriteBtn) {
            this.saveFavoriteBtn.addEventListener('click', () => this.openSaveFavoriteModal());
        }
        this.loadFavorites();
    }

    initSaveFavoriteModal() {
        if (!this.saveFavoriteModal) {
            const modalEl = document.getElementById('saveFavoriteModal');
            if (!modalEl) return;
            this.saveFavoriteModal = new bootstrap.Modal(modalEl);
            this.favoriteNameInput = document.getElementById('favoriteNameInput');
            this.favoriteSelectionInfo = document.getElementById('favoriteSelectionInfo');
            this.confirmSaveFavoriteBtn = document.getElementById('confirmSaveFavoriteBtn');

            if (this.favoriteNameInput) {
                this.favoriteNameInput.addEventListener('input', () => {
                    const hasText = this.favoriteNameInput.value.trim().length > 0;
                    this.confirmSaveFavoriteBtn.disabled = !hasText;
                });
            }

            if (this.confirmSaveFavoriteBtn) {
                this.confirmSaveFavoriteBtn.addEventListener('click', () => this.handleSaveFavorite());
            }
        }
        // Update info
        if (this.favoriteSelectionInfo) {
            this.favoriteSelectionInfo.textContent = `${this.selectedPrompts.size} prompts will be saved in this favorite.`;
        }
    }

    openSaveFavoriteModal() {
        this.initSaveFavoriteModal();
        if (this.favoriteNameInput) {
            const defaultName = `Favorite (${this.selectedPrompts.size})`;
            this.favoriteNameInput.value = defaultName;
            this.confirmSaveFavoriteBtn.disabled = false;
        }
        if (this.saveFavoriteModal) this.saveFavoriteModal.show();
    }
    
    async loadFavorites() {
        try {
            const res = await fetch('/api/favorites');
            if (!res.ok) throw new Error('Failed to load favorites');
            const data = await res.json();
            this.favorites = data.favorites || [];
            this.renderFavoritesDropdown();
            // If SSR requested a favorite, apply it after load
            this.applyFavoriteFromSSR();
        } catch (e) {
            console.warn('Favorites load error:', e);
            this.renderFavoritesDropdown(true);
        }
    }

    applyFavoriteFromSSR() {
        try {
            const fid = window.__FAVORITE_ID_FROM_SSR__;
            if (!fid) return;
            const found = this.favorites.find(f => f.id === fid);
            if (found) {
                this.applyFavorite(fid);
                // ensure dropdown reflects merge off by default
                if (this.mergeFavoriteToggle) this.mergeFavoriteToggle.checked = false;
            }
        } catch (_) { /* ignore */ }
    }
    
    renderFavoritesDropdown(hasError = false) {
        if (!this.favoritesDropdownMenu) return;
        if (hasError) {
            this.favoritesDropdownMenu.innerHTML = '<li class="px-3 py-2 text-danger small">Failed to load favorites</li>';
            return;
        }
        if (!this.favorites || this.favorites.length === 0) {
            this.favoritesDropdownMenu.innerHTML = '<li class="px-3 py-2 text-muted small">No favorites yet</li>';
            return;
        }
        const itemsHtml = this.favorites.map(f => {
            const count = (f.items || []).length;
            return `
                <li>
                    <div class="dropdown-item d-flex justify-content-between align-items-center">
                        <button class="btn btn-link p-0 text-start apply-favorite-btn" data-id="${f.id}">
                            <i class="bi bi-play-circle me-2"></i>${this.escapeHtml(f.name)} <span class="text-muted">(${count})</span>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-favorite-btn" title="Delete" data-id="${f.id}"><i class="bi bi-trash"></i></button>
                    </div>
                </li>`;
        }).join('');
        this.favoritesDropdownMenu.innerHTML = itemsHtml;
        this.favoritesDropdownMenu.querySelectorAll('.apply-favorite-btn').forEach(btn => {
            btn.addEventListener('click', () => this.applyFavorite(parseInt(btn.dataset.id)));
        });
        this.favoritesDropdownMenu.querySelectorAll('.delete-favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                if (confirm('Delete this favorite?')) this.deleteFavorite(id);
            });
        });
    }
    
    escapeHtml(text) {
        return (text || '').replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[ch]));
    }
    
    async handleSaveFavorite() {
        if (this.selectedPrompts.size === 0) return;
        const name = (this.favoriteNameInput?.value || '').trim();
        if (!name) return;
        const promptIds = this.getSelectedPromptIdsInDomOrder();
        try {
            const res = await fetch('/api/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, prompt_ids: promptIds })
            });
            if (!res.ok) throw new Error('Failed to save favorite');
            this.showToast('Favorite saved!', 'success');
            if (this.saveFavoriteModal) this.saveFavoriteModal.hide();
            await this.loadFavorites();
        } catch (e) {
            console.error(e);
            this.showToast('Failed to save favorite', 'error');
        }
    }
    
    getSelectedPromptIdsInDomOrder() {
        // Collect according to current DOM order for predictable application
        const ids = [];
        document.querySelectorAll('.prompt-checkbox').forEach(cb => {
            if (cb.checked) ids.push(parseInt(cb.value));
        });
        return ids;
    }
    
    applyFavorite(favoriteId) {
        const favorite = this.favorites.find(f => f.id === favoriteId);
        if (!favorite) return;
        const merge = !!(this.mergeFavoriteToggle && this.mergeFavoriteToggle.checked);
        if (!merge) {
            this.checkboxes.forEach(cb => { if (cb.checked) { cb.checked = false; this.handleCheckboxChange(cb); } });
        }
        // Temporarily suppress pair auto-copy while applying many selections
        this.suppressCombinationCopy = true;
        (favorite.items || []).forEach(item => {
            const cb = document.getElementById(`prompt-${item.prompt_id}`);
            if (cb) { cb.checked = true; this.handleCheckboxChange(cb); }
        });
        this.suppressCombinationCopy = false;
        // Missing due to filters?
        const total = (favorite.items || []).length;
        const visible = (favorite.items || []).filter(it => document.getElementById(`prompt-${it.prompt_id}`)).length;
        if (visible < total) {
            this.showToast(`Applied favorite "${favorite.name}" (${visible}/${total}). Some prompts are hidden by filters.`, 'warning');
        } else {
            this.showToast(`Applied favorite "${favorite.name}"`, 'success');
        }

        // Show only favorite's prompts in the view
        const favoriteIds = new Set((favorite.items || []).map(i => parseInt(i.prompt_id)));
        this.filterViewToFavorite(favorite.name, favoriteIds);

        // Copy all selected into clipboard so multi-item favorites place full content (not just a pair)
        if (this.selectedPrompts.size > 0) {
            this.copyAllSelectedPrompts();
        }
    }

    /**
     * Hide all prompt cards except those in favoriteIds and show a dismissible banner.
     */
    filterViewToFavorite(favoriteName, favoriteIds) {
        const listContainer = document.getElementById('promptsList');
        if (!listContainer) return;
        listContainer.querySelectorAll('.col-12').forEach(col => {
            const checkbox = col.querySelector('.prompt-checkbox');
            if (!checkbox) return;
            const id = parseInt(checkbox.value);
            col.style.display = favoriteIds.has(id) ? '' : 'none';
        });

        this.renderFavoriteFilterBanner(favoriteName, favoriteIds.size);
        this.activeFavoriteFilter = { name: favoriteName, ids: favoriteIds };
    }

    renderFavoriteFilterBanner(favoriteName, count) {
        let banner = document.getElementById('favoriteFilterBanner');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'favoriteFilterBanner';
            banner.className = 'alert alert-info d-flex justify-content-between align-items-center';
            const parent = document.querySelector('.col-md-9');
            const promptsList = document.getElementById('promptsList');
            if (parent && promptsList) {
                parent.insertBefore(banner, promptsList);
            } else {
                document.body.prepend(banner);
            }
        }
        banner.innerHTML = `
            <div>
                <i class="bi bi-filter me-2"></i>
                Showing favorite <strong>"${this.escapeHtml(favoriteName)}"</strong> (${count}). All other prompts are hidden.
            </div>
            <div>
                <button class="btn btn-sm btn-outline-secondary" id="clearFavoriteFilterBtn">
                    <i class="bi bi-x-circle me-1"></i>Clear favorite filter
                </button>
            </div>
        `;
        const clearBtn = banner.querySelector('#clearFavoriteFilterBtn');
        clearBtn.addEventListener('click', () => this.clearFavoriteFilter());
    }

    clearFavoriteFilter() {
        const listContainer = document.getElementById('promptsList');
        if (listContainer) {
            listContainer.querySelectorAll('.col-12').forEach(col => {
                col.style.display = '';
            });
        }
        const banner = document.getElementById('favoriteFilterBanner');
        if (banner) banner.remove();
        this.activeFavoriteFilter = null;
    }
    
    async deleteFavorite(favoriteId) {
        try {
            const res = await fetch(`/api/favorites/${favoriteId}`, { method: 'DELETE' });
            if (res.status === 204) {
                this.showToast('Favorite deleted', 'success');
                this.favorites = this.favorites.filter(f => f.id !== favoriteId);
                this.renderFavoritesDropdown();
            } else {
                this.showToast('Failed to delete favorite', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showToast('Failed to delete favorite', 'error');
        }
    }
    
    /**
     * Initialize combined content panel functionality
     */
    initCombinedContentPanel() {
        if (!this.combinedContentPanel || !this.combinedContentTextarea) {
            return;
        }
        
        // Initialize clear combined button
        if (this.clearCombinedBtn) {
            this.clearCombinedBtn.addEventListener('click', () => this.clearCombinedContent());
        }
        
        // Initialize copy combined button
        if (this.copyCombinedBtn) {
            this.copyCombinedBtn.addEventListener('click', () => this.copyCombinedContent());
        }
        
        // Initialize textarea input event for character/word counting
        if (this.combinedContentTextarea) {
            this.combinedContentTextarea.addEventListener('input', () => this.updateTextCounts());
        }
    }
    
    /**
     * Update combined content panel visibility and content
     */
    updateCombinedContentPanel() {
        const selectedCount = this.selectedPrompts.size;
        
        // Only show panel if it's visible
        if (!this.isPanelVisible) {
            this.hideCombinedContentPanel();
            return;
        }
        
        this.showCombinedContentPanel();
        
        if (selectedCount === 0) {
            // Show empty state message
            this.showEmptyPanelState();
        } else {
            this.updateCombinedContent();
            this.updateSelectedCount(selectedCount);
        }
    }
    
    /**
     * Show combined content panel
     */
    showCombinedContentPanel() {
        if (this.combinedContentPanel) {
            this.combinedContentPanel.style.display = 'block';
            this.combinedContentPanel.classList.add('fade-in');
            this.isPanelVisible = true;
        }
    }
    
    /**
     * Hide combined content panel
     */
    hideCombinedContentPanel() {
        if (this.combinedContentPanel) {
            this.combinedContentPanel.classList.add('slide-up');
            setTimeout(() => {
                this.combinedContentPanel.style.display = 'none';
                this.combinedContentPanel.classList.remove('slide-up');
            }, 300);
            this.isPanelVisible = false;
        }
    }
    
    /**
     * Update combined content in textarea
     */
    updateCombinedContent() {
        if (!this.combinedContentTextarea) {
            return;
        }
        
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
            this.combinedContentTextarea.value = combinedContent;
            this.combinedContentTextarea.placeholder = 'Edit combined content here...';
            this.updateTextCounts();
        }
    }
    
    /**
     * Update selected count badge
     */
    updateSelectedCount(count) {
        if (this.selectedCountBadge) {
            this.selectedCountBadge.textContent = count;
        }
    }
    
    /**
     * Show empty state in combined content panel
     */
    showEmptyPanelState() {
        if (this.combinedContentTextarea) {
            this.combinedContentTextarea.value = '';
            this.combinedContentTextarea.placeholder = 'Select prompts to see their combined content here...';
        }
        if (this.selectedCountBadge) {
            this.selectedCountBadge.textContent = '0';
        }
        if (this.copyCombinedBtn) {
            this.copyCombinedBtn.disabled = true;
        }
        this.updateTextCounts();
    }
    
    /**
     * Update character and word counts
     */
    updateTextCounts() {
        if (!this.combinedContentTextarea || !this.charCountSpan || !this.wordCountSpan) {
            return;
        }
        
        const text = this.combinedContentTextarea.value;
        const charCount = text.length;
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        
        this.charCountSpan.textContent = charCount;
        this.wordCountSpan.textContent = wordCount;
        
        // Update copy button state
        if (this.copyCombinedBtn) {
            this.copyCombinedBtn.disabled = charCount === 0;
        }
    }
    
    /**
     * Copy combined content to clipboard
     */
    copyCombinedContent() {
        if (!this.combinedContentTextarea) {
            return;
        }
        
        const content = this.combinedContentTextarea.value;
        if (content.trim()) {
            this.copyToClipboard(content, this.copyCombinedBtn);
            this.showToast('Combined content copied to clipboard!', 'success');
        } else {
            this.showToast('No content to copy', 'warning');
        }
    }
    
    /**
     * Clear combined content
     */
    clearCombinedContent() {
        if (this.combinedContentTextarea) {
            this.combinedContentTextarea.value = '';
            this.updateTextCounts();
        }
        this.showToast('Combined content cleared', 'info');
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
            
            // Clear combined content panel
            this.clearCombinedContent();
            
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
        
        // Ctrl/Cmd + P for toggle combined content panel
        if ((event.ctrlKey || event.metaKey) && event.key === 'p') {
            event.preventDefault();
            this.toggleCombinedContentPanel();
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

    /**
     * Initialize panel toggle button
     */
    initPanelToggleButton() {
        if (this.toggleCombinedPanelBtn) {
            this.toggleCombinedPanelBtn.addEventListener('click', () => this.toggleCombinedContentPanel());
        }
    }

    /**
     * Toggle combined content panel visibility
     */
    toggleCombinedContentPanel() {
        this.isPanelVisible = !this.isPanelVisible;
        this.savePanelVisibilityPreference();

        if (this.isPanelVisible) {
            this.showCombinedContentPanel();
            this.toggleCombinedPanelBtn.innerHTML = '<i class="bi bi-chevron-up me-1"></i>Hide Panel';
            this.toggleCombinedPanelBtn.setAttribute('title', 'Hide combined content panel');
            this.toggleCombinedPanelBtn.classList.add('active');
            this.updateCombinedContentPanel(); // Update content if there are selected prompts
        } else {
            this.hideCombinedContentPanel();
            this.toggleCombinedPanelBtn.innerHTML = '<i class="bi bi-chevron-down me-1"></i>Show Panel';
            this.toggleCombinedPanelBtn.setAttribute('title', 'Show combined content panel');
            this.toggleCombinedPanelBtn.classList.remove('active');
        }
        
        // Reinitialize tooltip
        this.reinitializeTooltip(this.toggleCombinedPanelBtn);
    }

    /**
     * Save panel visibility preference to localStorage
     */
    savePanelVisibilityPreference() {
        localStorage.setItem('combinedPanelVisible', this.isPanelVisible);
    }

    /**
     * Initialize tag filter functionality
     */
    initTagFilters() {
        const tagFilters = document.querySelectorAll('.tag-filter');
        tagFilters.forEach(tag => {
            tag.addEventListener('click', (e) => this.handleTagFilterClick(e));
            tag.addEventListener('keydown', (e) => this.handleTagFilterKeydown(e));
            
            // Ensure tags are focusable
            tag.setAttribute('tabindex', '0');
            tag.setAttribute('role', 'button');
            tag.setAttribute('aria-label', `Filter by tag: ${tag.getAttribute('data-tag')}`);
        });
    }

    /**
     * Handle tag filter click with parameter preservation
     */
    handleTagFilterClick(event) {
        event.preventDefault();
        this.applyTagFilter(event.currentTarget);
    }
    
    /**
     * Handle keyboard navigation for tag filters
     */
    handleTagFilterKeydown(event) {
        const tagElement = event.currentTarget;
        const tagFilters = Array.from(document.querySelectorAll('.tag-filter'));
        const currentIndex = tagFilters.indexOf(tagElement);
        
        switch (event.key) {
            case 'Enter':
            case ' ':
                event.preventDefault();
                this.applyTagFilter(tagElement);
                break;
                
            case 'ArrowRight':
            case 'ArrowDown':
                event.preventDefault();
                const nextIndex = (currentIndex + 1) % tagFilters.length;
                tagFilters[nextIndex].focus();
                break;
                
            case 'ArrowLeft':
            case 'ArrowUp':
                event.preventDefault();
                const prevIndex = currentIndex === 0 ? tagFilters.length - 1 : currentIndex - 1;
                tagFilters[prevIndex].focus();
                break;
                
            case 'Home':
                event.preventDefault();
                tagFilters[0].focus();
                break;
                
            case 'End':
                event.preventDefault();
                tagFilters[tagFilters.length - 1].focus();
                break;
                
            case 'Escape':
                event.preventDefault();
                tagElement.blur();
                break;
        }
    }
    
    /**
     * Apply tag filter (common logic for click and keyboard)
     */
    applyTagFilter(tagElement) {
        const tagName = tagElement.getAttribute('data-tag');
        
        // Get current URL and parameters
        const url = new URL(window.location.href);
        const params = url.searchParams;

        // Toggle tag in the query params (add if missing, remove if present)
        const currentTags = params.getAll('tags');
        if (currentTags.includes(tagName)) {
            const remaining = currentTags.filter(t => t !== tagName);
            params.delete('tags');
            [...new Set(remaining)].forEach(t => params.append('tags', t));
        } else {
            params.append('tags', tagName);
        }

        // Navigate to the updated URL with preserved parameters
        window.location.href = url.toString();
    }

    /**
     * Restore panel visibility preference from localStorage
     */
    restorePanelVisibility() {
        if (this.toggleCombinedPanelBtn) {
            this.isPanelVisible = this.panelVisibilityPreference;
            if (this.isPanelVisible) {
                this.showCombinedContentPanel();
                this.toggleCombinedPanelBtn.innerHTML = '<i class="bi bi-chevron-up me-1"></i>Hide Panel';
                this.toggleCombinedPanelBtn.setAttribute('title', 'Hide combined content panel');
                this.toggleCombinedPanelBtn.classList.add('active');
            } else {
                this.hideCombinedContentPanel();
                this.toggleCombinedPanelBtn.innerHTML = '<i class="bi bi-chevron-down me-1"></i>Show Panel';
                this.toggleCombinedPanelBtn.setAttribute('title', 'Show combined content panel');
                this.toggleCombinedPanelBtn.classList.remove('active');
            }
        }
    }
    
    /**
     * Initialize drag and drop functionality
     */
    initDragAndDrop() {
        const promptsList = document.getElementById('promptsList');
        if (!promptsList) {
            return;
        }
        
        // Initialize SortableJS
        this.sortable = Sortable.create(promptsList, {
            animation: 150,
            handle: '.drag-handle',  // Only allow dragging from the handle
            draggable: '.col-12',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            
            // Store initial order
            onStart: (evt) => {
                // Add visual feedback
                evt.item.style.opacity = '0.4';
                document.body.style.cursor = 'grabbing';
            },
            
            // Restore visual state
            onEnd: (evt) => {
                evt.item.style.opacity = '';
                document.body.style.cursor = '';
                
                // Only save if position actually changed
                if (evt.oldIndex !== evt.newIndex) {
                    this.savePromptsOrder();
                }
            }
        });
    }
    
    /**
     * Save the new order of prompts to the server
     */
    savePromptsOrder() {
        // Get all prompt cards in their current order
        const promptCards = document.querySelectorAll('.prompt-card');
        const orderedIds = [];
        
        promptCards.forEach(card => {
            const checkbox = card.querySelector('.prompt-checkbox');
            if (checkbox) {
                orderedIds.push(parseInt(checkbox.value));
            }
        });
        
        // Show loading state
        this.showToast('Saving new order...', 'info');
        
        // Send the new order to the server
        fetch('/prompts/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ordered_ids: orderedIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast('Order saved successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to save order');
            }
        })
        .catch(error => {
            console.error('Error saving order:', error);
            this.showToast('Failed to save order. Please try again.', 'error');
            
            // Optionally reload to restore original order
            if (confirm('Failed to save the new order. Reload page to restore original order?')) {
                window.location.reload();
            }
        });
    }
    
    /**
     * Initialize status filter listener for dynamic tag updates
     */
    initStatusFilterListener() {
        const statusInputs = document.querySelectorAll('input[name="is_active"]');
        statusInputs.forEach(input => {
            input.addEventListener('change', (e) => this.handleStatusFilterChange(e));
        });
    }
    
    /**
     * Handle status filter change and update tags accordingly
     */
    async handleStatusFilterChange(event) {
        const newStatus = event.target.value;
        if (newStatus !== this.currentStatusFilter) {
            this.currentStatusFilter = newStatus;
            await this.updatePopularTags(newStatus);
        }
    }
    
    /**
     * Update popular tags based on current status filter
     */
    async updatePopularTags(status) {
        try {
            this.showTagLoadingState();
            const response = await fetch(`/api/tags/popular?is_active=${status}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderPopularTags(data.tags);
            } else {
                console.error('Failed to fetch tags:', data.error);
                this.showTagErrorState();
            }
        } catch (error) {
            console.error('Error updating tags:', error);
            this.showTagErrorState();
        }
    }
    
    /**
     * Render popular tags in the container with enhanced count indicators
     */
    renderPopularTags(tags) {
        if (!this.tagFiltersContainer) return;
        
        if (tags.length === 0) {
            this.tagFiltersContainer.innerHTML = `
                <div class="text-center py-3">
                    <small class="text-muted">No tags found for current status</small>
                </div>
            `;
            return;
        }
        
        // Determine currently selected tags from URL
        const url = new URL(window.location.href);
        const selectedTags = url.searchParams.getAll('tags');

        this.tagFiltersContainer.innerHTML = tags.map(tag => {
            const countClass = this.getCountClass(tag.usage_count);
            const countText = this.formatCount(tag.usage_count);
            const isSelected = selectedTags.includes(tag.name);
            const selectedClass = isSelected ? ' selected' : '';
            const ariaPressed = isSelected ? 'true' : 'false';
            
            return `
                <a href="#" 
                   class="tag tag-filter theme-transition${selectedClass}" 
                   data-tag="${tag.name}"
                   style="background-color: ${tag.color}"
                   title="${tag.name} - ${tag.usage_count} prompt${tag.usage_count !== 1 ? 's' : ''}"
                   tabindex="0"
                   role="button"
                   aria-label="Filter by tag: ${tag.name} (${tag.usage_count} prompt${tag.usage_count !== 1 ? 's' : ''})"
                   aria-pressed="${ariaPressed}">
                    <span class="tag-name">${tag.name}</span>
                    <span class="tag-count ${countClass}" aria-label="${tag.usage_count} prompt${tag.usage_count !== 1 ? 's' : ''}">${countText}</span>
                </a>
            `;
        }).join('');
        
        // Reinitialize tag click handlers
        this.initTagFilters();
    }

    /**
     * Sync selected state of Popular Tags with URL parameters (defensive enhancement for SSR mismatches)
     */
    syncSelectedTagVisualsWithURL() {
        try {
            const url = new URL(window.location.href);
            const selectedTags = new Set(url.searchParams.getAll('tags'));
            const tagFilters = document.querySelectorAll('.tag-filter');
            tagFilters.forEach(tagEl => {
                const name = tagEl.getAttribute('data-tag');
                const isSelected = selectedTags.has(name);
                tagEl.classList.toggle('selected', isSelected);
                tagEl.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
            });
        } catch (e) {
            console.warn('Failed to sync tag visuals with URL:', e);
        }
    }
    
    /**
     * Get CSS class for count styling based on usage count
     */
    getCountClass(count) {
        if (count === 0) return 'count-zero';
        if (count <= 2) return 'count-low';
        if (count <= 5) return 'count-medium';
        return 'count-high';
    }
    
    /**
     * Format count display with appropriate styling
     */
    formatCount(count) {
        if (count === 0) return '0';
        if (count > 99) return '99+';
        return count.toString();
    }
    
    /**
     * Show loading state for tag updates
     */
    showTagLoadingState() {
        if (!this.tagFiltersContainer) return;
        this.tagFiltersContainer.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Loading tags...</span>
                </div>
                <small class="d-block mt-2 text-muted">Updating tags...</small>
            </div>
        `;
    }
    
    /**
     * Show error state for tag updates
     */
    showTagErrorState() {
        if (!this.tagFiltersContainer) return;
        this.tagFiltersContainer.innerHTML = `
            <div class="text-center py-3">
                <small class="text-muted">Failed to load tags. Please refresh the page.</small>
            </div>
        `;
    }
    
    /**
     * Get current status filter value
     */
    getCurrentStatusFilter() {
        const checkedInput = document.querySelector('input[name="is_active"]:checked');
        return checkedInput ? checkedInput.value : 'all';
    }
    
    /**
     * Initialize attached prompt functionality
     */
    initAttachedPrompts() {
        this.initAttachedPromptCards();
        this.initAttachPromptButtons();
        this.initDetachPromptButtons();
    }
    
    /**
     * Initialize attached prompt cards
     */
    initAttachedPromptCards() {
        const attachedCards = document.querySelectorAll('.attached-prompt-card');
        
        attachedCards.forEach(card => {
            // Add click handler for the entire card
            card.addEventListener('click', (e) => {
                if (e.target.closest('.select-combination-btn')) {
                    this.handleAttachedPromptSelection(card);
                }
            });
            
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.cursor = 'pointer';
            });
        });
    }
    
    /**
     * Handle selection of attached prompt combination
     */
    async handleAttachedPromptSelection(card) {
        const mainId = card.dataset.mainId;
        const attachedId = card.dataset.attachedId;
        
        // Select both prompts
        const mainCheckbox = document.getElementById(`prompt-${mainId}`);
        const attachedCheckbox = document.getElementById(`prompt-${attachedId}`);
        
        if (mainCheckbox && attachedCheckbox) {
            mainCheckbox.checked = true;
            attachedCheckbox.checked = true;
            
            // Trigger change events to update UI
            mainCheckbox.dispatchEvent(new Event('change'));
            attachedCheckbox.dispatchEvent(new Event('change'));
            
            // Visual feedback
            card.classList.add('selecting');
            setTimeout(() => card.classList.remove('selecting'), 600);
            
            // Use the unified combination copy logic
            await this.handleCombinationCopy(mainId, attachedId);
        } else {
            this.showToast('Error: Could not find prompt checkboxes', 'error');
        }
    }
    
    /**
     * Get prompt content via API
     */
    async getPromptContent(promptId) {
        try {
            const response = await fetch(`/api/prompts/${promptId}`);
            if (response.ok) {
                const data = await response.json();
                return data.prompt;
            }
            return null;
        } catch (error) {
            console.error('Error fetching prompt:', error);
            return null;
        }
    }
    
    /**
     * Handle combination copy using existing formatCombinedContent logic
     */
    async handleCombinationCopy(mainId, attachedId) {
        try {
            const [mainPrompt, attachedPrompt] = await Promise.all([
                this.getPromptContent(mainId),
                this.getPromptContent(attachedId)
            ]);
            
            if (mainPrompt && attachedPrompt) {
                // Use the same formatCombinationContent method for consistency
                const combinedContent = this.formatCombinationContent(
                    mainPrompt.content, 
                    attachedPrompt.content, 
                    mainPrompt.title, 
                    attachedPrompt.title
                );
                
                // Copy to clipboard
                this.copyToClipboard(combinedContent, document.querySelector(`#prompt-${mainId}`));
                
                // Show success message
                this.showToast('Combination selected and copied to clipboard!', 'success');
                
                // Increment usage count
                this.incrementCombinationUsage(mainId, attachedId);
            } else {
                this.showToast('Error: Could not load prompt content', 'error');
            }
        } catch (error) {
            console.error('Error handling combination copy:', error);
            this.showToast('Error: Could not load prompt content', 'error');
        }
    }
    
    /**
     * Format combination content for clipboard
     */
    formatCombinationContent(mainContent, attachedContent, mainTitle, attachedTitle) {
        // Use the existing formatCombinedContent method for consistency
        const selectedContents = [
            { content: mainContent, title: mainTitle },
            { content: attachedContent, title: attachedTitle }
        ];
        return this.formatCombinedContent(selectedContents);
    }
    
    /**
     * Increment usage count for combination
     */
    async incrementCombinationUsage(mainId, attachedId) {
        try {
            const response = await fetch(`/api/prompts/${mainId}/attach/${attachedId}/use`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                console.warn('Failed to increment usage count:', response.status);
            }
        } catch (error) {
            console.warn('Error incrementing usage count:', error);
        }
    }
    
    /**
     * Initialize attach prompt buttons
     */
    initAttachPromptButtons() {
        console.log('🔗 Initializing attach prompt buttons...');
        const attachButtons = document.querySelectorAll('.attach-prompt-btn');
        console.log('Found attach buttons:', attachButtons.length);
        
        attachButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                console.log('🔘 Attach button clicked!');
                e.preventDefault();
                const promptId = button.dataset.promptId;
                console.log('Prompt ID:', promptId);
                
                // Debug the condition
                console.log('🔍 Condition check:');
                console.log('  - attachMode:', this.attachMode);
                console.log('  - promptId:', promptId);
                console.log('  - mainPromptId:', this.mainPromptId);
                console.log('  - promptId != mainPromptId:', promptId != this.mainPromptId);
                console.log('  - attachMode && promptId != mainPromptId:', this.attachMode && promptId != this.mainPromptId);
                
                // If we're in attach mode and this is not the main prompt, attach it
                if (this.attachMode && parseInt(promptId) != this.mainPromptId) {
                                console.log('🎯 In attach mode, attaching prompt:', promptId);
            this.attachPromptToMain(parseInt(promptId));
                } else if (!this.attachMode) {
                    // If not in attach mode, enter attach mode
                    console.log('🔄 Entering attach mode for prompt:', promptId);
                    this.toggleAttachMode(promptId, button);
                } else {
                    // If in attach mode and this is the main prompt, do nothing
                    console.log('⏭️ Already in attach mode for this prompt, ignoring click');
                }
            });
        });
    }
    
    /**
     * Toggle attach mode for a prompt
     */
    toggleAttachMode(promptId, button) {
        console.log('🔄 toggleAttachMode called with promptId:', promptId);
        console.log('Current attachMode:', this.attachMode);
        
        // If already in attach mode and this is the same prompt, cancel it
        if (this.attachMode && parseInt(promptId) == this.mainPromptId) {
            console.log('Already in attach mode for this prompt, cancelling...');
            this.cancelAttachMode();
            return;
        }
        
        // Enter attach mode
        console.log('🟢 Entering attach mode for prompt:', promptId);
        this.attachMode = true;
        this.mainPromptId = parseInt(promptId);
        
        // Update button appearance
        button.innerHTML = '<i class="bi bi-x-circle"></i>';
        button.className = 'btn btn-sm btn-danger attach-prompt-btn';
        button.setAttribute('title', 'Cancel attachment mode');
        
        // Show instructions
        this.showAttachInstructions();
        
        // No need to add separate click handlers - they're handled in initAttachPromptButtons
        
        // Add class to body for styling
        document.body.classList.add('attach-mode-active');
        console.log('✅ Attach mode activated successfully');
    }
    
    /**
     * Cancel attach mode
     */
    cancelAttachMode() {
        this.attachMode = false;
        this.mainPromptId = null;
        
        // Reset all attach buttons
        const attachButtons = document.querySelectorAll('.attach-prompt-btn');
        attachButtons.forEach(button => {
            button.innerHTML = '<i class="bi bi-link-45deg"></i>';
            button.className = 'btn btn-sm btn-outline-info attach-prompt-btn';
            button.setAttribute('title', 'Attach another prompt');
            button.onclick = null; // Remove temporary handlers
        });
        
        // Hide instructions
        this.hideAttachInstructions();
        
        // No need to reinitialize - buttons are handled by the main click handler
        
        // Remove class from body
        document.body.classList.remove('attach-mode-active');
    }
    
    /**
     * Show attach instructions
     */
    showAttachInstructions() {
        // Show existing instructions panel
        const instructionsPanel = document.getElementById('attachInstructionsPanel');
        if (instructionsPanel) {
            const mainPromptTitle = this.getPromptTitle(this.mainPromptId);
            instructionsPanel.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>🔗 Attachment Mode Active</strong><br>
                        Main prompt: <strong>${mainPromptTitle}</strong><br>
                        Click "Attach" on another prompt to attach it to this one
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-secondary" onclick="window.promptListManager.cancelAttachMode()">
                        <i class="bi bi-x-circle me-1"></i>Cancel
                    </button>
                </div>
            `;
            instructionsPanel.style.display = 'block';
        }
    }
    
    /**
     * Hide attach instructions
     */
    hideAttachInstructions() {
        const instructionsPanel = document.getElementById('attachInstructionsPanel');
        if (instructionsPanel) {
            instructionsPanel.style.display = 'none';
        }
    }
    
    /**
     * Add click handlers for attachment
     */
    addAttachClickHandlers() {
        console.log('🔗 Adding click handlers to other attach buttons...');
        const attachButtons = document.querySelectorAll('.attach-prompt-btn');
        let handlerCount = 0;
        
        attachButtons.forEach(button => {
            const promptId = button.dataset.promptId;
            
            // Skip the main prompt button
            if (promptId == this.mainPromptId) {
                console.log('⏭️ Skipping main prompt button:', promptId);
                return;
            }
            
            // Add temporary click handler
            button.onclick = (e) => {
                console.log('🎯 Secondary attach button clicked for prompt:', promptId);
                e.preventDefault();
                e.stopPropagation();
                this.attachPromptToMain(promptId);
            };
            handlerCount++;
        });
        
        console.log(`✅ Added ${handlerCount} click handlers to other buttons`);
    }
    
    /**
     * Attach a prompt to the main prompt
     */
    async attachPromptToMain(attachedPromptId) {
        console.log('🔗 Starting attachment process...');
        console.log('Main prompt ID:', this.mainPromptId);
        console.log('Attached prompt ID:', attachedPromptId);
        
        try {
            const mainTitle = this.getPromptTitle(this.mainPromptId);
            const attachedTitle = this.getPromptTitle(attachedPromptId);
            
            console.log('Main prompt title:', mainTitle);
            console.log('Attached prompt title:', attachedTitle);
            
            // Show confirmation
            if (!confirm(`Attach "${attachedTitle}" to "${mainTitle}"?`)) {
                console.log('❌ User cancelled attachment');
                return;
            }
            
            // Show loading state
            this.showToast('Attaching prompt...', 'info');
            
            console.log('📡 Making API request to:', `/api/prompts/${this.mainPromptId}/attach`);
            
            const response = await fetch(`/api/prompts/${this.mainPromptId}/attach`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attached_prompt_id: attachedPromptId
                })
            });
            
            console.log('📡 Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ API Error:', errorData);
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📊 Response data:', data);
            
            if (data.success) {
                console.log('✅ Attachment successful!');
                this.showToast(`Successfully attached "${attachedTitle}" to "${mainTitle}"!`, 'success');
                this.cancelAttachMode();
                
                // Refresh the page to show updated attached prompts
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.error('❌ API returned success=false:', data);
                throw new Error(data.error || 'Failed to attach prompt');
            }
            
        } catch (error) {
            console.error('❌ Attach error:', error);
            this.showToast(`Failed to attach prompt: ${error.message}`, 'error');
        }
    }
    
    /**
     * Get prompt title by ID
     */
    getPromptTitle(promptId) {
        const promptCard = document.querySelector(`[data-prompt-id="${promptId}"]`) || 
                          document.querySelector(`.prompt-card[data-prompt-id="${promptId}"]`);
        
        if (promptCard) {
            const titleElement = promptCard.querySelector('.card-title');
            if (titleElement) {
                return titleElement.textContent.trim();
            }
        }
        
        return `Prompt ${promptId}`;
    }
    
    // Removed showAttachPromptModal - now using toggleAttachMode
    
    /**
     * Load available prompts for attachment
     */
    async loadAvailablePrompts(mainPromptId, searchQuery = '') {
        const listContainer = document.getElementById('availablePromptsList');
        
        try {
            let url = `/api/prompts/${mainPromptId}/attached/available`;
            if (searchQuery) {
                url += `?search=${encodeURIComponent(searchQuery)}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.renderAvailablePrompts(data.data, mainPromptId);
            } else {
                listContainer.innerHTML = '<div class="text-center text-danger">Failed to load prompts</div>';
            }
        } catch (error) {
            console.error('Error loading available prompts:', error);
            listContainer.innerHTML = '<div class="text-center text-danger">Error loading prompts</div>';
        }
    }
    
    /**
     * Render available prompts in the modal
     */
    renderAvailablePrompts(prompts, mainPromptId) {
        const listContainer = document.getElementById('availablePromptsList');
        
        if (prompts.length === 0) {
            listContainer.innerHTML = '<div class="text-center text-muted">No prompts available for attachment</div>';
            return;
        }
        
        const promptsHtml = prompts.map(prompt => `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${prompt.title}</h6>
                    <small class="text-muted">${prompt.content.substring(0, 100)}${prompt.content.length > 100 ? '...' : ''}</small>
                </div>
                <button class="btn btn-sm btn-primary attach-prompt-item-btn" 
                        data-prompt-id="${prompt.id}" 
                        data-main-prompt-id="${mainPromptId}">
                    Attach
                </button>
            </div>
        `).join('');
        
        listContainer.innerHTML = promptsHtml;
        
        // Add click handlers for attach buttons
        listContainer.querySelectorAll('.attach-prompt-item-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const promptId = btn.dataset.promptId;
                this.attachPrompt(mainPromptId, promptId);
            });
        });
    }
    
    /**
     * Setup search functionality in the modal
     */
    setupPromptSearch(mainPromptId) {
        const searchInput = document.getElementById('promptSearch');
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.loadAvailablePrompts(mainPromptId, e.target.value);
            }, 300);
        });
    }
    
    /**
     * Attach a prompt to another prompt
     */
    async attachPrompt(mainPromptId, attachedPromptId) {
        try {
            const response = await fetch(`/api/prompts/${mainPromptId}/attach`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attached_prompt_id: parseInt(attachedPromptId)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Prompt attached successfully!', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('attachPromptModal'));
                modal.hide();
                
                // Reload page to show new attachment
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.showToast(data.error || 'Failed to attach prompt', 'error');
            }
        } catch (error) {
            console.error('Error attaching prompt:', error);
            this.showToast('Error attaching prompt', 'error');
        }
    }
    
    /**
     * Initialize detach prompt buttons
     */
    initDetachPromptButtons() {
        const detachButtons = document.querySelectorAll('.detach-prompt-btn');
        
        detachButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const card = button.closest('.attached-prompt-card');
                const mainId = card.dataset.mainId;
                const attachedId = card.dataset.attachedId;
                
                if (confirm('Are you sure you want to detach this prompt?')) {
                    this.detachPrompt(mainId, attachedId);
                }
            });
        });
    }
    
    /**
     * Detach a prompt from another prompt
     */
    async detachPrompt(mainPromptId, attachedPromptId) {
        try {
            const response = await fetch(`/api/prompts/${mainPromptId}/attach/${attachedPromptId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Prompt detached successfully!', 'success');
                
                // Remove the card from DOM
                const card = document.querySelector(`[data-main-id="${mainPromptId}"][data-attached-id="${attachedPromptId}"]`);
                if (card) {
                    card.remove();
                    
                    // Update attachment count
                    const container = card.closest('.attached-prompts-container');
                    if (container) {
                        const remainingCards = container.querySelectorAll('.attached-prompt-card');
                        const header = container.querySelector('.attached-prompts-header small');
                        if (header) {
                            header.innerHTML = `<i class="bi bi-link-45deg me-1"></i>Attached Prompts (${remainingCards.length})`;
                        }
                        
                        // Hide container if no more attachments
                        if (remainingCards.length === 0) {
                            container.style.display = 'none';
                        }
                    }
                }
            } else {
                this.showToast(data.error || 'Failed to detach prompt', 'error');
            }
        } catch (error) {
            console.error('Error detaching prompt:', error);
            this.showToast('Error detaching prompt', 'error');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the prompts list page
    if (document.querySelector('.prompt-card')) {
        window.promptListManager = new PromptListManager();
    }
});

// Global functions for filter removal (called from HTML)
window.removeTagFilter = function(tagName) {
    const url = new URL(window.location);
    const currentTags = url.searchParams.getAll('tags');
    const newTags = currentTags.filter(tag => tag !== tagName);
    
    // Remove all tags parameters and add back the remaining ones
    url.searchParams.delete('tags');
    newTags.forEach(tag => url.searchParams.append('tags', tag));
    
    window.location.href = url.toString();
};

window.removeSearchFilter = function() {
    const url = new URL(window.location);
    url.searchParams.delete('search');
    window.location.href = url.toString();
};

window.removeStatusFilter = function() {
    const url = new URL(window.location);
    url.searchParams.delete('is_active');
    window.location.href = url.toString();
};

// Export for potential use in other modules
window.PromptListManager = PromptListManager;

 