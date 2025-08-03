/**
 * Theme Service for Prompt Manager
 * Handles theme switching, persistence, and system preference detection
 */

class ThemeService {
    constructor() {
        this.currentTheme = 'light';
        this.themeToggle = null;
        this.storageKey = 'prompt-manager-theme';
        this.themeAttribute = 'data-theme';
        this.supportedThemes = ['light', 'dark', 'system'];
        
        this.init();
    }
    
    /**
     * Initialize the theme service
     */
    init() {
        this.loadTheme();
        this.setupEventListeners();
        this.updateThemeToggle();
        
        // Only apply theme if not already set by early detection
        if (!document.documentElement.hasAttribute(this.themeAttribute)) {
            this.applyTheme();
        }
    }
    
    /**
     * Load theme from localStorage or system preference
     */
    loadTheme() {
        try {
            const savedTheme = localStorage.getItem(this.storageKey);
            if (savedTheme && this.supportedThemes.includes(savedTheme)) {
                this.currentTheme = savedTheme;
            } else {
                // Default to system preference
                this.currentTheme = 'system';
            }
        } catch (error) {
            console.warn('Failed to load theme from localStorage:', error);
            this.currentTheme = 'system';
        }
    }
    
    /**
     * Save theme preference to localStorage
     */
    saveTheme() {
        try {
            localStorage.setItem(this.storageKey, this.currentTheme);
        } catch (error) {
            console.warn('Failed to save theme to localStorage:', error);
        }
    }
    
    /**
     * Get the effective theme (resolves 'system' to actual theme)
     */
    getEffectiveTheme() {
        if (this.currentTheme === 'system') {
            return this.getSystemTheme();
        }
        return this.currentTheme;
    }
    
    /**
     * Detect system theme preference
     */
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    /**
     * Apply the current theme to the document
     */
    applyTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        const html = document.documentElement;
        
        // Check if theme is already applied
        if (html.getAttribute(this.themeAttribute) === effectiveTheme) {
            return;
        }
        
        // Add loading state
        html.classList.add('theme-loading');
        
        // Apply theme attribute
        html.setAttribute(this.themeAttribute, effectiveTheme);
        
        // Update theme toggle state
        this.updateThemeToggle();
        
        // Dispatch custom event
        this.dispatchThemeChangeEvent(effectiveTheme);
        
        // Remove loading state after transition
        setTimeout(() => {
            html.classList.remove('theme-loading');
        }, 300);
    }
    
    /**
     * Set theme and persist preference
     */
    setTheme(theme) {
        if (!this.supportedThemes.includes(theme)) {
            console.warn(`Unsupported theme: ${theme}`);
            return;
        }
        
        this.currentTheme = theme;
        this.saveTheme();
        this.applyTheme();
    }
    
    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        const newTheme = effectiveTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
    
    /**
     * Cycle through themes: light -> dark -> system -> light
     */
    cycleTheme() {
        const currentIndex = this.supportedThemes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % this.supportedThemes.length;
        this.setTheme(this.supportedThemes[nextIndex]);
    }
    
    /**
     * Update theme toggle button state
     */
    updateThemeToggle() {
        if (!this.themeToggle) return;
        
        const effectiveTheme = this.getEffectiveTheme();
        this.themeToggle.setAttribute(this.themeAttribute, effectiveTheme);
        
        // Update ARIA attributes for better accessibility
        const nextTheme = effectiveTheme === 'light' ? 'dark' : 'light';
        const ariaLabel = `Switch to ${nextTheme} theme. Current theme is ${effectiveTheme}`;
        const ariaPressed = effectiveTheme === 'dark' ? 'true' : 'false';
        
        this.themeToggle.setAttribute('aria-label', ariaLabel);
        this.themeToggle.setAttribute('aria-pressed', ariaPressed);
        this.themeToggle.setAttribute('title', ariaLabel);
        
        // Update role for better screen reader support
        this.themeToggle.setAttribute('role', 'button');
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Find theme toggle button
        this.themeToggle = document.querySelector('.theme-toggle');
        
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
            
            // Keyboard support
            this.themeToggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });
        }
        
        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', () => {
                if (this.currentTheme === 'system') {
                    this.applyTheme();
                }
            });
        }
        
        // Listen for storage changes (for multi-tab support)
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey && e.newValue) {
                this.currentTheme = e.newValue;
                this.applyTheme();
            }
        });
    }
    
    /**
     * Dispatch custom theme change event
     */
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: {
                theme: theme,
                previousTheme: this.currentTheme
            }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    /**
     * Check if current theme is dark
     */
    isDark() {
        return this.getEffectiveTheme() === 'dark';
    }
    
    /**
     * Check if current theme is light
     */
    isLight() {
        return this.getEffectiveTheme() === 'light';
    }
    
    /**
     * Check if using system preference
     */
    isSystem() {
        return this.currentTheme === 'system';
    }
    
    /**
     * Add theme-aware class to element
     */
    addThemeClass(element, className) {
        if (!element) return;
        
        const effectiveTheme = this.getEffectiveTheme();
        element.classList.add(`${className}-${effectiveTheme}`);
    }
    
    /**
     * Remove theme-aware class from element
     */
    removeThemeClass(element, className) {
        if (!element) return;
        
        this.supportedThemes.forEach(theme => {
            element.classList.remove(`${className}-${theme}`);
        });
    }
}

// Initialize theme service when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeService = new ThemeService();
    
    // Add page transition effects
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.classList.add('page-transition');
        // Trigger loaded state after a short delay
        setTimeout(() => {
            mainContent.classList.add('loaded');
        }, 100);
    }
    
    // Add enhanced hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('theme-hover-lift');
    });
    
    // Add focus ring improvements to interactive elements
    const focusableElements = document.querySelectorAll('button, input, select, textarea, a[href]');
    focusableElements.forEach(element => {
        element.classList.add('theme-focus-ring');
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeService;
} 