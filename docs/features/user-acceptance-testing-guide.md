# User Acceptance Testing Guide - Contextual Tag Filtering

## Overview

This guide provides comprehensive testing scenarios and validation criteria for the Contextual Tag Filtering feature. It covers all user interactions, edge cases, and accessibility requirements to ensure the feature meets user expectations and business requirements.

## Test Environment Setup

### Prerequisites
- Application running on `http://localhost:5001`
- Sample data with various tags and prompts (active/inactive)
- Different browsers (Chrome, Firefox, Safari, Edge)
- Screen reader software (NVDA, JAWS, VoiceOver)
- Mobile devices for responsive testing

### Test Data Requirements
- At least 10 different tags
- Mix of active and inactive prompts
- Tags used in both active and inactive prompts
- Tags used only in active prompts
- Tags used only in inactive prompts
- Empty scenarios (no tags, no prompts)

## Test Scenarios

### Scenario 1: Basic Functionality Testing

#### 1.1 Initial Page Load
**Objective**: Verify correct initial state
**Steps**:
1. Navigate to `/prompts` page
2. Check default status filter (should be "All")
3. Verify popular tags are displayed
4. Check tag counts match total usage

**Expected Results**:
- ✅ Status filter defaults to "All"
- ✅ All tags are visible with correct counts
- ✅ Tag colors and styling are correct
- ✅ No loading indicators visible

#### 1.2 Status Filter Change - Active
**Objective**: Test switching to Active status
**Steps**:
1. Click "Active" radio button
2. Observe tag container for loading state
3. Verify tags update to show only active-related tags
4. Check tag counts reflect only active prompts

**Expected Results**:
- ✅ Loading spinner appears briefly
- ✅ Tags update smoothly with transition
- ✅ Only tags with active prompts are shown
- ✅ Tag counts show only active prompt usage
- ✅ No tags with 0 count are displayed

#### 1.3 Status Filter Change - Inactive
**Objective**: Test switching to Inactive status
**Steps**:
1. Click "Inactive" radio button
2. Observe tag container for loading state
3. Verify tags update to show only inactive-related tags
4. Check tag counts reflect only inactive prompts

**Expected Results**:
- ✅ Loading spinner appears briefly
- ✅ Tags update smoothly with transition
- ✅ Only tags with inactive prompts are shown
- ✅ Tag counts show only inactive prompt usage
- ✅ No tags with 0 count are displayed

#### 1.4 Status Filter Change - All
**Objective**: Test switching back to All status
**Steps**:
1. Click "All" radio button
2. Observe tag container for loading state
3. Verify all tags are displayed again
4. Check tag counts reflect total usage

**Expected Results**:
- ✅ Loading spinner appears briefly
- ✅ All tags are visible again
- ✅ Tag counts show total usage across all statuses
- ✅ Smooth transition animation

### Scenario 2: Tag Interaction Testing

#### 2.1 Tag Click Functionality
**Objective**: Verify tag filtering works correctly
**Steps**:
1. Select a status filter (Active/Inactive/All)
2. Click on a tag
3. Verify URL updates with tag parameter
4. Check prompt list filters correctly

**Expected Results**:
- ✅ URL includes selected tag parameter
- ✅ Prompt list shows only prompts with selected tag
- ✅ Status filter remains selected
- ✅ Selected tag is visually highlighted

#### 2.2 Multiple Tag Selection
**Objective**: Test selecting multiple tags
**Steps**:
1. Select a status filter
2. Click on first tag
3. Click on second tag
4. Verify both tags are applied

**Expected Results**:
- ✅ URL includes both tag parameters
- ✅ Prompt list shows prompts matching either tag
- ✅ Both tags are visually highlighted

#### 2.3 Tag Count Validation
**Objective**: Verify tag counts are accurate
**Steps**:
1. Note tag count for a specific tag
2. Apply that tag filter
3. Count actual prompts in results
4. Compare with displayed count

**Expected Results**:
- ✅ Tag count matches actual prompt count
- ✅ Counts update correctly when status changes
- ✅ Zero counts are handled gracefully

### Scenario 3: Error Handling Testing

#### 3.1 Network Error Simulation
**Objective**: Test behavior during network failures
**Steps**:
1. Open browser developer tools
2. Simulate offline mode or network error
3. Change status filter
4. Observe error handling

**Expected Results**:
- ✅ Error message is displayed
- ✅ User is informed to refresh page
- ✅ Previous tags remain visible
- ✅ No broken UI state

#### 3.2 Slow Network Simulation
**Objective**: Test behavior with slow connections
**Steps**:
1. Use browser dev tools to throttle network
2. Change status filter rapidly
3. Observe loading states and transitions

**Expected Results**:
- ✅ Loading indicators are visible
- ✅ Multiple rapid changes are handled gracefully
- ✅ No duplicate requests or race conditions
- ✅ Smooth user experience maintained

#### 3.3 Invalid API Response
**Objective**: Test handling of malformed responses
**Steps**:
1. Use browser dev tools to modify API responses
2. Change status filter
3. Observe error handling

**Expected Results**:
- ✅ Error message is displayed
- ✅ Application remains functional
- ✅ User can continue using other features

### Scenario 4: Accessibility Testing

#### 4.1 Keyboard Navigation
**Objective**: Verify keyboard accessibility
**Steps**:
1. Use Tab key to navigate through status filters
2. Use Tab key to navigate through tags
3. Use Enter/Space to activate tags
4. Use Arrow keys for navigation

**Expected Results**:
- ✅ All interactive elements are focusable
- ✅ Focus indicators are visible
- ✅ Keyboard shortcuts work correctly
- ✅ Screen reader announces changes

#### 4.2 Screen Reader Testing
**Objective**: Verify screen reader compatibility
**Steps**:
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Navigate through status filters
3. Navigate through tags
4. Listen to announcements

**Expected Results**:
- ✅ Status changes are announced
- ✅ Tag names and counts are read
- ✅ Loading states are announced
- ✅ Error messages are accessible

#### 4.3 High Contrast Mode
**Objective**: Test high contrast accessibility
**Steps**:
1. Enable high contrast mode
2. Navigate through all features
3. Verify visibility and readability

**Expected Results**:
- ✅ All elements are visible
- ✅ Text is readable
- ✅ Interactive elements are distinguishable
- ✅ Loading states are visible

#### 4.4 Reduced Motion Testing
**Objective**: Test reduced motion accessibility
**Steps**:
1. Enable reduced motion in OS settings
2. Change status filters
3. Observe transitions

**Expected Results**:
- ✅ Animations are disabled or reduced
- ✅ Functionality remains intact
- ✅ No motion sickness triggers

### Scenario 5: Performance Testing

#### 5.1 Response Time Validation
**Objective**: Verify performance requirements
**Steps**:
1. Use browser dev tools to measure response times
2. Change status filters multiple times
3. Record average response times

**Expected Results**:
- ✅ API responses complete within 500ms
- ✅ DOM updates complete within 200ms
- ✅ Smooth 60fps animations
- ✅ No noticeable lag or stuttering

#### 5.2 Memory Usage Testing
**Objective**: Check for memory leaks
**Steps**:
1. Open browser dev tools memory tab
2. Change status filters repeatedly
3. Monitor memory usage

**Expected Results**:
- ✅ No memory leaks detected
- ✅ Memory usage remains stable
- ✅ No excessive DOM elements created

#### 5.3 Large Dataset Testing
**Objective**: Test with large amounts of data
**Steps**:
1. Create 100+ tags and prompts
2. Test status filter changes
3. Monitor performance

**Expected Results**:
- ✅ Performance remains acceptable
- ✅ UI remains responsive
- ✅ Loading states work correctly

### Scenario 6: Cross-Browser Testing

#### 6.1 Chrome Testing
**Steps**:
1. Test all scenarios in Chrome
2. Verify functionality and appearance
3. Check console for errors

#### 6.2 Firefox Testing
**Steps**:
1. Test all scenarios in Firefox
2. Verify functionality and appearance
3. Check console for errors

#### 6.3 Safari Testing
**Steps**:
1. Test all scenarios in Safari
2. Verify functionality and appearance
3. Check console for errors

#### 6.4 Edge Testing
**Steps**:
1. Test all scenarios in Edge
2. Verify functionality and appearance
3. Check console for errors

### Scenario 7: Mobile Responsive Testing

#### 7.1 Mobile Browser Testing
**Objective**: Test on mobile devices
**Steps**:
1. Test on iOS Safari
2. Test on Android Chrome
3. Test touch interactions

**Expected Results**:
- ✅ Touch targets are appropriately sized
- ✅ No horizontal scrolling required
- ✅ All functionality works on touch
- ✅ Performance is acceptable

#### 7.2 Tablet Testing
**Objective**: Test on tablet devices
**Steps**:
1. Test on iPad Safari
2. Test on Android tablet
3. Test both orientations

**Expected Results**:
- ✅ Layout adapts to screen size
- ✅ Touch interactions work correctly
- ✅ Performance is good

## Validation Checklist

### Functional Requirements
- [ ] Tags update automatically when status filter changes
- [ ] Only relevant tags are shown for current status
- [ ] Loading states are displayed during updates
- [ ] Error states are handled gracefully
- [ ] Backward compatibility is maintained
- [ ] Tag counts are accurate
- [ ] Multiple tag selection works
- [ ] URL parameters are correct

### Performance Requirements
- [ ] Tag updates complete within 500ms
- [ ] No layout shift during updates
- [ ] Smooth animations (60fps)
- [ ] Graceful degradation for slow connections
- [ ] No memory leaks
- [ ] Acceptable performance with large datasets

### UX Requirements
- [ ] Intuitive behavior (tags match current filter)
- [ ] Clear loading feedback
- [ ] Consistent with existing design
- [ ] Accessible to screen readers
- [ ] Keyboard navigation support
- [ ] Touch-friendly on mobile
- [ ] High contrast mode support
- [ ] Reduced motion support

### Accessibility Requirements
- [ ] All interactive elements are focusable
- [ ] Focus indicators are visible
- [ ] Screen reader announcements work
- [ ] Keyboard shortcuts function correctly
- [ ] High contrast mode is supported
- [ ] Reduced motion is respected
- [ ] ARIA attributes are correct
- [ ] Semantic HTML is used

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers
- [ ] Tablet browsers

## Bug Reporting Template

When reporting issues, include:

```
**Bug Title**: [Brief description]

**Environment**:
- Browser: [Chrome/Firefox/Safari/Edge]
- Version: [Version number]
- OS: [Windows/Mac/Linux/iOS/Android]
- Screen size: [Desktop/Tablet/Mobile]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]

**Actual Result**: [What actually happens]

**Screenshots**: [If applicable]

**Console Errors**: [Any JavaScript errors]

**Additional Notes**: [Any other relevant information]
```

## Test Data Setup Script

```python
# Sample script to create test data
from app import create_app
from app.models.tag import Tag
from app.models.prompt import Prompt
from app.models.base import db

def create_test_data():
    app = create_app('development')
    with app.app_context():
        # Create tags
        tags = [
            Tag(name="python", color="#3776ab"),
            Tag(name="javascript", color="#f7df1e"),
            Tag(name="sql", color="#e48e00"),
            Tag(name="html", color="#e34f26"),
            Tag(name="css", color="#1572b6"),
            Tag(name="react", color="#61dafb"),
            Tag(name="vue", color="#4fc08d"),
            Tag(name="angular", color="#dd0031"),
            Tag(name="nodejs", color="#339933"),
            Tag(name="docker", color="#2496ed")
        ]
        
        for tag in tags:
            db.session.add(tag)
        db.session.commit()
        
        # Create prompts with different statuses
        prompts = [
            Prompt(title="Python Guide", content="Python tutorial", is_active=True),
            Prompt(title="JS Tutorial", content="JavaScript guide", is_active=True),
            Prompt(title="SQL Basics", content="SQL introduction", is_active=False),
            Prompt(title="HTML Intro", content="HTML basics", is_active=True),
            Prompt(title="CSS Styling", content="CSS guide", is_active=False),
            Prompt(title="React App", content="React tutorial", is_active=True),
            Prompt(title="Vue Basics", content="Vue.js guide", is_active=False),
            Prompt(title="Angular Setup", content="Angular tutorial", is_active=True),
            Prompt(title="Node.js API", content="Node.js guide", is_active=False),
            Prompt(title="Docker Container", content="Docker tutorial", is_active=True)
        ]
        
        for prompt in prompts:
            db.session.add(prompt)
        db.session.commit()
        
        # Associate tags with prompts
        prompts[0].tags = [tags[0], tags[1]]  # python, javascript (active)
        prompts[1].tags = [tags[1], tags[3]]  # javascript, html (active)
        prompts[2].tags = [tags[2]]           # sql (inactive)
        prompts[3].tags = [tags[3], tags[4]]  # html, css (active + inactive)
        prompts[4].tags = [tags[4]]           # css (inactive)
        prompts[5].tags = [tags[5], tags[1]]  # react, javascript (active)
        prompts[6].tags = [tags[6]]           # vue (inactive)
        prompts[7].tags = [tags[7], tags[8]]  # angular, nodejs (active + inactive)
        prompts[8].tags = [tags[8]]           # nodejs (inactive)
        prompts[9].tags = [tags[9], tags[0]]  # docker, python (active)
        
        db.session.commit()
        print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()
```

## Success Criteria

The feature is considered successfully implemented when:

1. **All functional requirements are met** (100% pass rate)
2. **Performance requirements are satisfied** (response times < 500ms)
3. **Accessibility requirements are fulfilled** (WCAG 2.1 AA compliance)
4. **Cross-browser compatibility is achieved** (all major browsers)
5. **Mobile responsiveness is confirmed** (all screen sizes)
6. **No critical bugs remain** (only minor cosmetic issues allowed)
7. **User feedback is positive** (intuitive and helpful)

## Sign-off Process

- [ ] **QA Lead**: All test scenarios passed
- [ ] **Accessibility Specialist**: WCAG compliance confirmed
- [ ] **UX Designer**: User experience validated
- [ ] **Product Owner**: Business requirements met
- [ ] **Technical Lead**: Code quality and performance approved

---

**Document Version**: 1.0  
**Created**: [Current Date]  
**Last Updated**: [Current Date]  
**Status**: Ready for UAT Execution 