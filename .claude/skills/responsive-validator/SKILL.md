---
name: responsive-validator
description: Validates UI responsiveness across all viewport sizes (300px to 2560px)
version: 1.0.0
owner: ui-auth-expert
tags: [ui, responsive, validation, next.js, tailwind]
---

# Responsive Validator Skill

## Purpose
Automatically validate that all UI components are responsive and functional across the full range of viewport sizes from 300px (mobile) to 2560px (wide desktop).

## Scope
- **Owned By**: @ui-auth-expert
- **Technology Stack**: Next.js, Tailwind CSS, React
- **Validation Range**: 300px - 2560px viewport width

## Mandatory Checks

### 1. Viewport Breakpoints
- **Mobile**: 300px - 639px
- **Tablet**: 640px - 1023px
- **Desktop**: 1024px - 1919px
- **Wide Desktop**: 1920px - 2560px

### 2. Validation Criteria
- [ ] No horizontal scroll at any breakpoint
- [ ] All text is readable (min 14px font size on mobile)
- [ ] Interactive elements have min 44x44px touch targets on mobile
- [ ] Images scale proportionally without distortion
- [ ] Navigation is accessible at all sizes
- [ ] Forms are usable without horizontal scrolling
- [ ] Modals/dialogs fit within viewport
- [ ] Flexbox/Grid layouts adapt properly

### 3. Tailwind CSS Standards
- Use responsive utility classes (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- Prefer `max-w-*` for content containers
- Use `overflow-hidden` or `overflow-auto` appropriately
- Leverage `flex-wrap` for flexible layouts

## Execution Protocol

When invoked, this skill will:
1. Identify all React components in the `frontend/` directory
2. Check for responsive Tailwind classes
3. Flag components without mobile-first responsive design
4. Generate a validation report with pass/fail status
5. Provide specific remediation steps for failures

## Usage

```bash
# Validate all components
/responsive-validator

# Validate specific component
/responsive-validator --component TodoList

# Generate detailed report
/responsive-validator --report
```

## Success Criteria
- ✅ 100% of components pass responsive validation
- ✅ No layout breaks at any tested breakpoint
- ✅ All interactive elements meet accessibility standards
- ✅ Performance budget maintained (<100ms layout shift)

## Integration
This skill integrates with:
- **@ui-auth-expert**: Primary owner and executor
- **@qa-automation**: Automated regression testing
- **@performance-optimizer**: Layout shift monitoring
