# Theme System Implementation Guide

## Overview
This guide provides comprehensive documentation for the theme system implementation in the Prompt Manager application. It covers architecture, usage, maintenance, and best practices.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Implementation Details](#implementation-details)
3. [Usage Guidelines](#usage-guidelines)
4. [Maintenance and Updates](#maintenance-and-updates)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)
7. [Testing Guidelines](#testing-guidelines)

## Architecture Overview

### Core Components
The theme system consists of three main components:

1. **CSS Architecture** (`app/static/css/style.css`)
   - CSS Custom Properties for theme variables
   - Theme-specific overrides using `[data-theme]` selectors
   - Utility classes for consistent theming

2. **JavaScript Theme Service** (`app/static/js/theme-service.js`)
   - Theme detection and switching logic
   - Local storage persistence
   - System preference detection
   - Event dispatching for theme changes

3. **HTML Integration** (`app/templates/base.html`)
   - Theme toggle button
   - Early theme detection script
   - Theme-aware class application

### Theme Variables Structure
```css
:root {
    /* Light theme defaults */
    --primary-color: #3B82F6;
    --background-color: #F9FAFB;
    --surface-color: #FFFFFF;
    /* ... other variables */
}

[data-theme="dark"] {
    /* Dark theme overrides */
    --primary-color: #3B82F6;
    --background-color: #0F172A;
    --surface-color: #1E293B;
    /* ... other variables */
}
```

## Implementation Details

### CSS Custom Properties
The theme system uses CSS custom properties (variables) to define theme-specific values:

#### Color Variables
- **Primary Colors**: Brand colors and main UI elements
- **Status Colors**: Success, warning, danger, info states
- **Background Colors**: Page and component backgrounds
- **Text Colors**: Primary, secondary, and muted text
- **Border Colors**: Component borders and dividers

#### Spacing and Typography
- **Spacing Scale**: Consistent spacing values (xs, sm, md, lg, xl, 2xl)
- **Typography Scale**: Font sizes and weights
- **Border Radius**: Component corner radius values
- **Shadows**: Elevation and depth indicators

### JavaScript Theme Service
The `ThemeService` class provides:

#### Core Methods
- `initialize()`: Set up theme system on page load
- `loadTheme()`: Load theme from localStorage
- `setTheme(theme)`: Apply specific theme
- `toggleTheme()`: Switch between light and dark
- `updateToggleButton()`: Update UI to reflect current theme

#### Event Handling
- System theme preference changes
- Storage events for multi-tab synchronization
- Custom `themechange` events for application integration

### HTML Integration
The base template includes:

#### Early Theme Detection
```html
<script>
    // Prevent FOUC by setting theme before CSS loads
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', savedTheme || systemTheme);
</script>
```

#### Theme Toggle Button
```html
<button id="theme-toggle" data-theme-toggle aria-label="Toggle theme">
    <i class="theme-icon-light"></i>
    <i class="theme-icon-dark"></i>
</button>
```

## Usage Guidelines

### For Developers

#### Adding New Components
When creating new components, follow these guidelines:

1. **Use CSS Variables**
```css
.new-component {
    background-color: var(--surface-color);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}
```

2. **Apply Theme Classes**
```html
<div class="new-component theme-surface theme-text theme-border">
    <!-- Component content -->
</div>
```

3. **Consider Interactive States**
```css
.new-component:hover {
    background-color: var(--surface-hover);
    border-color: var(--border-hover);
}
```

#### Theme-Aware Utility Classes
Use the provided utility classes for consistent theming:

- **Background**: `.theme-bg`, `.theme-surface`
- **Text**: `.theme-text`, `.theme-text-secondary`
- **Borders**: `.theme-border`
- **Spacing**: `.theme-spacing-*`
- **Typography**: `.theme-text-*`
- **Shadows**: `.theme-shadow-*`

### For Designers

#### Color Palette Guidelines
- **Primary Colors**: Use for main actions and branding
- **Status Colors**: Use consistently for feedback states
- **Background Colors**: Maintain proper contrast ratios
- **Text Colors**: Ensure readability in both themes

#### Component Design
- **Consistent Spacing**: Use the defined spacing scale
- **Border Radius**: Apply consistent corner radius
- **Shadows**: Use elevation system for depth
- **Transitions**: Apply smooth theme transitions

## Maintenance and Updates

### Adding New Themes
To add a new theme (e.g., "auto" or custom themes):

1. **Add CSS Variables**
```css
[data-theme="auto"] {
    /* Auto theme variables */
    --primary-color: #3B82F6;
    --background-color: #F9FAFB;
    /* ... other variables */
}
```

2. **Update JavaScript Service**
```javascript
// Add theme detection logic
if (theme === 'auto') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    this.applyTheme(systemTheme);
}
```

3. **Update HTML Template**
```html
<!-- Add theme option to toggle -->
<button data-theme="auto">Auto</button>
```

### Updating Color Palettes
When updating colors:

1. **Test Contrast Ratios**: Ensure WCAG 2.1 AA compliance
2. **Update Both Themes**: Maintain consistency across themes
3. **Document Changes**: Update design system documentation
4. **Test Thoroughly**: Verify in all components and states

### Performance Optimization
- **Minimize CSS**: Use efficient selectors and avoid redundancy
- **Optimize JavaScript**: Debounce theme switching events
- **Lazy Load**: Load theme-specific assets on demand
- **Cache Results**: Store computed theme values

## Troubleshooting

### Common Issues

#### Flash of Unstyled Content (FOUC)
**Problem**: Brief flash of default theme before user preference loads
**Solution**: 
- Ensure early theme detection script is in `<head>`
- Use CSS visibility control: `html:not([data-theme]) { visibility: hidden; }`

#### Theme Not Persisting
**Problem**: Theme preference resets on page reload
**Solution**:
- Check localStorage availability
- Verify theme service initialization
- Ensure proper error handling

#### Inconsistent Styling
**Problem**: Some components don't follow theme
**Solution**:
- Use CSS variables instead of hardcoded colors
- Apply theme-aware utility classes
- Check for CSS specificity conflicts

#### Performance Issues
**Problem**: Slow theme switching or page load
**Solution**:
- Optimize CSS selectors
- Minimize JavaScript execution
- Use efficient DOM manipulation

### Debugging Tools

#### Browser Developer Tools
1. **Inspect CSS Variables**: Check computed styles for CSS custom properties
2. **Test Theme Switching**: Use console to manually set `data-theme` attribute
3. **Check localStorage**: Verify theme preference storage
4. **Monitor Performance**: Use Performance tab for timing analysis

#### Testing Scripts
- Run `python scripts/visual_testing.py` for automated testing
- Use `python scripts/test_theme_performance.py` for performance testing
- Follow `scripts/user_testing_guide.md` for manual testing

## Best Practices

### CSS Best Practices
1. **Use Semantic Variable Names**: `--primary-color` instead of `--blue`
2. **Maintain Consistent Structure**: Group related variables together
3. **Provide Fallbacks**: Use default values for older browsers
4. **Optimize Selectors**: Use efficient CSS selectors for performance

### JavaScript Best Practices
1. **Error Handling**: Gracefully handle localStorage and media query errors
2. **Event Management**: Properly clean up event listeners
3. **Performance**: Debounce rapid theme switching events
4. **Accessibility**: Ensure keyboard navigation and screen reader support

### HTML Best Practices
1. **Semantic Structure**: Use proper HTML elements and attributes
2. **Accessibility**: Include ARIA labels and roles
3. **Progressive Enhancement**: Work without JavaScript when possible
4. **SEO**: Ensure proper meta tags and structure

### Design Best Practices
1. **Consistency**: Maintain visual consistency across themes
2. **Accessibility**: Ensure sufficient contrast ratios
3. **User Experience**: Provide smooth transitions and feedback
4. **Performance**: Optimize for fast loading and switching

## Testing Guidelines

### Automated Testing
1. **Unit Tests**: Test individual theme service methods
2. **Integration Tests**: Test theme system with application
3. **Visual Tests**: Automated visual regression testing
4. **Performance Tests**: Measure theme switching performance

### Manual Testing
1. **Cross-Browser Testing**: Test in all supported browsers
2. **Responsive Testing**: Test on different screen sizes
3. **Accessibility Testing**: Test with screen readers and keyboard navigation
4. **User Testing**: Gather feedback from actual users

### Testing Checklist
- [ ] Theme switching works correctly
- [ ] Theme preference persists across sessions
- [ ] System preference detection works
- [ ] All components follow theme correctly
- [ ] Performance is acceptable
- [ ] Accessibility requirements are met
- [ ] Cross-browser compatibility verified
- [ ] Responsive design works in both themes

## Conclusion

The theme system provides a robust, accessible, and maintainable solution for light and dark themes. By following the guidelines in this document, developers can ensure consistent implementation and optimal user experience.

For questions or issues, refer to the troubleshooting section or consult the design system documentation for specific component guidelines. 