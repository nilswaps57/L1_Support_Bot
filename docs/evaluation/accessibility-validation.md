# Accessibility Validation

**Scope:** Phase 15B frontend accessibility checks
**Review date:** 2026-08-27

## Automated checks

`frontend/tests/e2e/accessibility.spec.ts` covers:

- Chat and Documents landmarks, labels, keyboard focus, and responsive reflow
- Configuration form labels and keyboard reachability
- Loading and error announcement roles
- Active navigation state through `aria-current`
- Mobile navigation disclosure through `aria-expanded`
- Native citation disclosure and source metadata
- Heading structure for the chat and citation view
- Destructive-dialog accessible name and modal semantics
- Dialog initial focus, Tab wrapping, Escape handling, and focus return

The focused Playwright accessibility spec passed with 7 tests. The frontend component suite
and production build also passed. No axe dependency was added; these checks do not change
runtime UI behavior.

## Manual checks not claimed

The following require a browser, assistive technology, or human reviewer and are not certified
by the automated suite:

- Screen-reader announcements and reading order in a supported browser
- Full keyboard-only traversal through every configuration action and error recovery path
- Visual focus indicator visibility at all responsive widths
- Text resizing/browser zoom and reflow at 200% or higher
- Contrast inspection for text, controls, status indicators, and focus boundaries
- Reduced-motion behavior with the operating-system preference enabled
- Touch target sizing and mobile assistive-technology gestures

These checks should be completed during release review. The current result is automated
readiness evidence, not a WCAG conformance or accessibility certification claim.
