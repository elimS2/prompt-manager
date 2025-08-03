# Design System Documentation

## Overview
This document outlines the design system for the Prompt Manager application, including color palettes, typography, spacing, and component guidelines for both light and dark themes.

## Color System

### Primary Colors
- **Primary Blue**: `#3B82F6` - Main brand color
- **Primary Hover**: `#2563EB` - Hover state
- **Primary Light**: `#DBEAFE` - Light variant (light theme)
- **Primary Dark**: `#1E40AF` - Dark variant (dark theme)

### Status Colors
- **Success**: `#10B981` (light) / `#059669` (dark)
- **Warning**: `#F59E0B` (light) / `#D97706` (dark)
- **Danger**: `#EF4444` (light) / `#DC2626` (dark)
- **Info**: `#3B82F6` (light) / `#3B82F6` (dark)

### Background Colors
- **Background**: `#F9FAFB` (light) / `#0F172A` (dark)
- **Surface**: `#FFFFFF` (light) / `#1E293B` (dark)
- **Surface Hover**: `#F9FAFB` (light) / `#334155` (dark)

### Text Colors
- **Primary Text**: `#111827` (light) / `#F8FAFC` (dark)
- **Secondary Text**: `#6B7280` (light) / `#E2E8F0` (dark)
- **Muted Text**: `#9CA3AF` (light) / `#94A3B8` (dark)
- **Inverse Text**: `#FFFFFF` (light) / `#0F172A` (dark)

### Border Colors
- **Border**: `#E5E7EB` (light) / `#475569` (dark)
- **Border Hover**: `#D1D5DB` (light) / `#64748B` (dark)
- **Border Focus**: `#3B82F6` (both themes)

## Typography

### Font Sizes
- **XS**: `0.75rem` (12px)
- **SM**: `0.875rem` (14px)
- **Base**: `1rem` (16px)
- **LG**: `1.125rem` (18px)
- **XL**: `1.25rem` (20px)
- **2XL**: `1.5rem` (24px)
- **3XL**: `1.875rem` (30px)

### Font Weights
- **Normal**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700

### Line Heights
- **Tight**: 1.25
- **Normal**: 1.5
- **Relaxed**: 1.75

## Spacing

### Spacing Scale
- **XS**: `0.25rem` (4px)
- **SM**: `0.5rem` (8px)
- **MD**: `1rem` (16px)
- **LG**: `1.5rem` (24px)
- **XL**: `2rem` (32px)
- **2XL**: `3rem` (48px)

## Border Radius

### Radius Scale
- **SM**: `0.25rem` (4px)
- **MD**: `0.375rem` (6px)
- **LG**: `0.5rem` (8px)
- **XL**: `0.75rem` (12px)

## Shadows

### Shadow Scale
- **SM**: `0 1px 2px rgba(0, 0, 0, 0.1)`
- **MD**: `0 4px 6px rgba(0, 0, 0, 0.1)`
- **LG**: `0 10px 15px rgba(0, 0, 0, 0.1)`
- **XL**: `0 20px 25px rgba(0, 0, 0, 0.1)`

## Component Guidelines

### Buttons
```css
.btn {
    border-radius: var(--border-radius-md);
    font-weight: 500;
    transition: all 0.3s ease;
    padding: var(--spacing-sm) var(--spacing-md);
}
```

### Cards
```css
.card {
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
    border: 1px solid var(--border-color);
}
```

### Form Controls
```css
.form-control {
    border-radius: var(--border-radius-md);
    transition: all 0.3s ease;
    border: 1px solid var(--border-color);
    padding: var(--spacing-sm);
}
```

### Tags
```css
.tag {
    border-radius: var(--border-radius-lg);
    font-size: var(--font-size-sm);
    font-weight: 500;
    padding: var(--spacing-xs) var(--spacing-sm);
}
```

## Interactive States

### Hover States
- **Cards**: Elevate with `translateY(-1px)` and increase shadow
- **Buttons**: Change background color and border
- **Links**: Change color with smooth transition

### Focus States
- **Outline**: 2px solid primary color
- **Offset**: 2px from element
- **Shadow**: Primary color with 25% opacity

### Active States
- **Buttons**: Return to original position
- **Cards**: Reduce shadow

## Animation Guidelines

### Transition Durations
- **Fast**: 0.15s
- **Normal**: 0.3s
- **Slow**: 0.5s

### Easing Functions
- **Linear**: `linear`
- **Ease In**: `ease-in`
- **Ease Out**: `ease-out`
- **Ease In Out**: `ease-in-out`

## Accessibility Guidelines

### Color Contrast
- **Normal Text**: Minimum 4.5:1 ratio
- **Large Text**: Minimum 3:1 ratio
- **UI Components**: Minimum 3:1 ratio

### Focus Indicators
- **Visible**: Always show focus indicators
- **Consistent**: Use same style across all interactive elements
- **High Contrast**: Ensure focus indicators are clearly visible

### Reduced Motion
- **Respect**: Honor `prefers-reduced-motion` setting
- **Fallback**: Provide static alternatives for animations
- **Essential**: Only animate essential interactions

## Theme Switching

### Smooth Transitions
- **Duration**: 0.3s for color changes
- **Properties**: background-color, color, border-color, box-shadow
- **Easing**: ease-in-out

### FOUC Prevention
- **Early Detection**: Apply theme before CSS loads
- **Fallback**: Default to light theme if detection fails
- **Graceful**: Handle errors without breaking layout

## Usage Guidelines

### CSS Variables
Always use CSS custom properties for theming:
```css
.element {
    background-color: var(--surface-color);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}
```

### Theme Classes
Use theme-aware utility classes:
```css
.theme-bg { background-color: var(--background-color); }
.theme-text { color: var(--text-primary); }
.theme-border { border-color: var(--border-color); }
```

### Component Consistency
Ensure all components follow the same patterns:
- Consistent spacing
- Consistent border radius
- Consistent shadows
- Consistent transitions

## Best Practices

### Color Usage
- Use semantic color names (success, warning, danger)
- Maintain consistent color relationships across themes
- Test color combinations for accessibility

### Typography
- Use consistent font sizes and weights
- Maintain proper line heights for readability
- Ensure text contrast meets accessibility standards

### Spacing
- Use the spacing scale consistently
- Maintain visual hierarchy through spacing
- Ensure responsive spacing on different screen sizes

### Shadows
- Use shadows to create depth and hierarchy
- Ensure shadows work in both light and dark themes
- Test shadow visibility and contrast

## Testing Guidelines

### Visual Testing
- Test all components in both themes
- Verify color contrast ratios
- Check focus indicator visibility
- Test with reduced motion preferences

### Accessibility Testing
- Use screen readers to test navigation
- Test keyboard-only navigation
- Verify color contrast with tools
- Test with high contrast mode

### Performance Testing
- Monitor theme switching performance
- Test with large numbers of elements
- Verify smooth animations
- Check for layout shifts

## Maintenance

### Regular Reviews
- Review color usage quarterly
- Update accessibility guidelines as needed
- Monitor for consistency issues
- Gather user feedback on theme experience

### Documentation Updates
- Keep this documentation current
- Document new components and patterns
- Update usage examples
- Maintain changelog of design system updates 