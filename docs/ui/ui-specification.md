# UI Specification: L1 Support Bot

## 1. Scope and Product Intent

This specification defines a focused visual and interaction system for the two existing frontend areas:

- **Branch User Chatbot**: ask FLEXCUBE support questions, read grounded answers, inspect sources, and manage the current session.
- **Configuration**: upload, inspect, monitor, re-index, and delete knowledge documents; provide a future home for grouped AI settings.

The application should feel like a dependable internal operations tool used daily on a laptop: quiet, structured, readable, and explicit about system state. The remediation preserves current React component behavior, routes, API payloads, response types, session rules, and document lifecycle rules.

## 2. Current UI Assessment

The implementation is functional and semantically recognizable, but presentation is mostly unstyled HTML. The main weaknesses are:

- `frontend/src/app/router.tsx` provides only a basic header and horizontal links; there is no persistent left navigation, active-section treatment, page context, breadcrumbs, or responsive shell.
- There are no source styles or design tokens in `frontend/src/`; spacing, type scale, focus treatment, color, borders, and state styling are undefined.
- `frontend/src/features/chatbot/pages/ChatPage.tsx` does not establish a clear work area for conversation, composer, session controls, or loading/service states.
- `MessageList`, `MessageBubble`, and `ChatInput` render user and assistant content as plain text. Long procedural answers have no reading width, structure, or visual role distinction.
- `ResponseState` and `ClarificationPrompt` expose important outcomes but do not provide a consistent alert/state pattern for grounded, partial, ambiguous, insufficient, expired-session, or service-failure cases.
- `CitationItem` exposes raw metadata including chunk identifiers. `CitationList` is not expandable and sources are not clearly separated from the answer.
- Configuration currently renders documents as an unordered list. `DocumentList` has no table columns, row-level action pattern, selection affordance, or structured loading/empty/error treatment.
- `DocumentUpload`, `DocumentStatus`, and `IngestionWarnings` communicate lifecycle information without a shared badge, alert, progress, or warning hierarchy.
- `DeleteDocumentDialog` has dialog semantics but no visible modal surface, focus management, escape handling, focus return, or destructive-action hierarchy.
- `/config` and `/config/ai` are route boundaries only. The shell should support grouped configuration sections without implying that credentials or secrets are editable or displayable.
- Existing component tests verify behavior and accessible names, but there are no responsive, keyboard-navigation, focus, screenshot, or visual-regression checkpoints.

## 3. Recommended Design Direction

Use a modern, restrained internal enterprise visual language:

- Neutral canvas with white content surfaces and one dark ink color for primary text.
- One cool operational accent for selected navigation and primary actions, plus semantic green, amber, red, and blue status colors. Do not use gradients, glass effects, decorative blobs, or consumer-style motion.
- Dense enough for document operations, with generous reading width and vertical rhythm for chat answers.
- Prefer explicit labels, visible state changes, and predictable placement over decorative iconography.
- Use icons only where they improve scanning; pair unfamiliar icons with accessible names and tooltips. Text remains for destructive and high-consequence actions.
- Motion is limited to a short page-load reveal and subtle loading shimmer where useful. Respect `prefers-reduced-motion`.

## 4. Design System

### 4.1 Application shell

- Full viewport shell with a fixed-width left rail on desktop and a compact top bar or off-canvas navigation on narrow widths.
- Left rail contains product identity, the two areas, and a small environment/product label. It remains visually quiet and does not compete with page content.
- Main area uses a responsive content container: approximately 1200px maximum, 24px to 40px desktop gutters, and 16px mobile gutters.
- Header row in the main area contains page context, optional actions, and session/context metadata. Avoid duplicating the rail label.
- Shell landmarks are explicit: `header`, `nav`, `main`, and, where used, complementary source/detail regions.

### 4.2 Left navigation

- Primary groups: **Branch User Chatbot** with `Chat`; **Configuration** with `Documents` and `AI configuration`.
- Active item has a solid, accessible selected treatment and `aria-current="page"`; hover and focus do not rely on color alone.
- The rail collapses at the mobile breakpoint behind a labeled menu button. Navigation closes after selection and remains keyboard reachable.
- Configuration subsections may be grouped visually without adding routes or API behavior.

### 4.3 Header, titles, and breadcrumbs

- Every page has one clear `h1`, a short supporting description where helpful, and a right-aligned page action area.
- Breadcrumbs appear for nested configuration pages, for example `Configuration / Documents`; the current page is plain text, not a dead link.
- Chat uses `Chat` as the title and `FLEXCUBE support` as supporting context. Documents uses a document-management description and a prominent upload action.
- Do not expose request IDs, model identifiers, checksums, or internal implementation metadata in the primary header.

### 4.4 Typography

Use a project-owned font stack with a readable sans-serif UI face and a system fallback; do not introduce a default browser-only hierarchy. Define these roles rather than styling individual tags ad hoc:

- Display/page title: 28px, 700, line-height 1.2.
- Section title: 18px, 650, line-height 1.3.
- Body: 15px, 400, line-height 1.55.
- Chat answer: 16px, 400, line-height 1.65, with a maximum reading width of roughly 72ch.
- Label and table metadata: 13px, 600 where emphasis is needed.
- Caption/helper text: 12px to 13px, 400.

Keep text zoom-friendly. Never use color alone to convey status. Avoid all-caps body text and avoid truncating required document names or answer content.

### 4.5 Color tokens

Define tokens in a global stylesheet so components consume roles, not raw colors. Initial roles should include:

- `--color-canvas`: cool, very light neutral page background.
- `--color-surface`: white surface.
- `--color-surface-muted`: subtle neutral panel background.
- `--color-ink`: high-contrast primary text.
- `--color-ink-muted`: secondary text with at least 4.5:1 contrast for normal text where used as meaningful content.
- `--color-border`: neutral divider and control border.
- `--color-border-strong`: selected/focused structural border.
- `--color-accent`: primary action and selected navigation.
- `--color-accent-contrast`: text/icon on accent backgrounds.
- `--color-info`, `--color-success`, `--color-warning`, `--color-danger` and corresponding `*-surface` tokens.
- `--color-focus`: a clearly visible focus ring distinct from borders.

Target WCAG 2.2 AA contrast: 4.5:1 for normal text, 3:1 for large text and meaningful graphical boundaries, and a visible 2px focus indicator with adequate offset.

### 4.6 Spacing, borders, radius, and elevation

Use a 4px base scale: `4, 8, 12, 16, 20, 24, 32, 40, 48`. Use 16px as the default control/content gap, 24px between page sections, and 32px to 40px around major page regions.

- Border: 1px solid tokenized neutral border.
- Radius: 4px for controls and fields; 6px for panels/dialogs; no pill shapes except compact status badges.
- Elevation: one restrained shadow token for dialogs and elevated menus; content sections remain mostly flat and separated by spacing/borders.
- Do not nest cards inside cards. Use unframed page bands and panels only where a boundary improves scanning.

### 4.7 Buttons and form controls

- Primary button: one per local workflow, used for `Ask`, `Upload`, and confirmation of a valid action.
- Secondary button: `Start new session`, `Re-index document`, or other non-destructive alternatives.
- Tertiary/text action: low-emphasis utility actions such as `Clear session` when context makes the action safe.
- Destructive button: danger treatment for delete confirmation only; never place it adjacent to the primary page action without separation.
- All buttons have stable height, visible focus, disabled/pending state, and no layout shift when their label changes.
- Textarea composer has a persistent label, useful minimum height, sensible max length behavior if already supported by the contract, and an obvious submit affordance. Enter behavior must be documented by the control behavior itself and remain keyboard accessible.
- Inputs/selects use consistent labels, helper/error text, and 44px minimum hit targets. File input may use a styled drop/select surface while retaining a real accessible file input.
- Never add controls for credentials, API keys, tokens, or secrets. Future AI forms use non-secret operational settings only unless a separate secure product decision exists.

### 4.8 Tables and structured lists

Configuration documents use a responsive table on laptop widths with columns for:

- Document name and type.
- Source type.
- Ingestion status.
- Indexed chunks.
- Updated date.
- Row action or selection affordance.

Use a semantic `<table>` with scoped column headers. Keep actions predictable and move the full detail view to a side panel or clearly bounded detail region without changing the existing query behavior. On narrow screens, transform rows into stacked labeled fields or allow controlled horizontal scrolling; do not hide status or destructive actions.

### 4.9 Status badges, alerts, and banners

- `DocumentStatus` becomes a compact status badge with a text label and optional non-color indicator. Active ingestion statuses show a subtle progress treatment and remain announced through an appropriate live region without repeated noisy announcements.
- Warnings use an amber alert surface with a concise summary and expandable details. Failures use a danger alert with the user-safe message already supplied by the API; do not surface tracebacks, paths, request metadata, or secrets.
- Success messages use a polite live region near the action that completed. Loading messages use `role="status"`; errors use `role="alert"` only for actionable failures.
- Alerts must not displace core controls unpredictably. Reserve or animate no space in a way that causes the composer or table actions to jump.

### 4.10 Modal dialogs

- Use a real modal surface with backdrop, `role="dialog"`, `aria-modal="true"`, a unique labelled heading, and a concise consequence statement.
- On open, focus the least destructive useful action or the dialog heading; trap focus within the modal, close on Escape, and return focus to the trigger on close.
- Delete confirmation has `Cancel` as the secondary action and `Delete document` as the clearly destructive action. Pending state disables both controls and exposes progress without changing dimensions.

### 4.11 Loading and empty states

- Initial chat session creation: page skeleton for the conversation frame plus a concise status that a session is being prepared. Composer is unavailable until a session exists.
- Chat response pending: preserve the submitted question, show an assistant loading state, and keep the composer stable.
- Chat empty state: brief, task-oriented prompt with the composer immediately available; no marketing copy.
- Document list loading: table-shaped skeleton preserving column proportions. Document detail loading: detail skeleton.
- Empty documents: explain that no sources are available and place the upload action in the same visual region.
- Service unavailable/error states: clear user-safe message, affected scope, and a retry or new-session action when supported by existing behavior.

### 4.12 Chat messages and response states

- Conversation is a readable vertical stream with consistent message grouping and generous separation.
- User messages use a restrained accent-tinted surface and a visible `You` label. Assistant messages use a neutral surface, visible `Support` label, and a distinct left rule or heading treatment. Do not rely on bubble color alone.
- Long procedural answers support paragraphs, ordered steps, lists, inline code-like values, and preserved line breaks without adding new backend parsing requirements. Limit line length and keep sources below the answer.
- Grounded answers show the answer first and sources second. Partial answers clearly identify what is supported and what is missing. Ambiguous answers foreground the clarification request. Incorrect-premise and insufficient-information states explain the limitation without implying unsupported certainty. Error answers use an alert treatment and keep the original question visible.
- Response state labels are short and consistent: `Supported`, `Partially supported`, `Clarification needed`, `Insufficient information`, `Premise not supported`, and `Unable to answer`.

### 4.13 Citation cards

- Replace the raw metadata list with an expandable `details/summary` card per source. Summary shows source name, source type where useful, and the strongest locator such as page or section.
- Expanded content presents available page, section, task, screen, menu, error, JIRA, RCA, and procedure context as labeled fields. Omit absent values and keep chunk IDs hidden from ordinary users unless there is a specific support workflow requiring them.
- Sources have their own heading/region and visual divider so they cannot be mistaken for assistant-authored answer text. Multiple sources remain individually identifiable.

### 4.14 Session controls

- Keep session status and `Clear session` in a compact toolbar associated with the chat header, not above every message.
- Show a human-readable expiry time with a stable label. Clearing starts a fresh session using the existing behavior and communicates completion in a polite status region.
- Expired-session state explains what happened and keeps `Start new session` as the dominant recovery action. Do not expose the session ID.

### 4.15 Responsive behavior

Support common laptop widths from 1024px upward and narrow widths down to 320px:

- At desktop widths, keep the left rail visible and use a two-region configuration detail layout only when it fits.
- Below approximately 900px, reduce shell gutters, allow the rail to collapse, and stack page actions.
- Below approximately 640px, use the mobile navigation trigger, stack upload fields, make the composer full width, and transform document rows into readable stacked records or controlled horizontal scrolling.
- Long filenames, source names, statuses, and buttons wrap without overlapping or causing controls to resize unexpectedly.
- Test at 1280x800, 1024x768, 768x1024, and 375x812. Include zoom/reflow checks at 200% where practical.

### 4.16 Accessibility

- Preserve semantic landmarks and heading order; use one `h1` per page.
- Every interactive control has an accessible name and a visible keyboard focus state. Keyboard order follows visual order.
- Use `aria-current` for navigation, labelled regions for conversation/sources/details, and live regions for loading, success, and actionable errors.
- Dialogs manage focus and announce their consequence. Expandable citations are keyboard-operable native disclosure controls.
- Status is conveyed through text plus icon/shape, never color alone. Ensure contrast for text, borders, focus, disabled controls, alerts, and selected navigation.
- Respect reduced motion and browser text zoom. Do not use hover-only information or remove native file-input keyboard access.
- Component tests cover names, roles, state announcements, disclosure behavior, dialog focus, keyboard paths, and preserved existing actions. Browser checks cover tab order, Escape, mobile navigation, and responsive overflow.

## 5. Component Strategy Decision

### Fluent UI React

**Strengths:** strong enterprise visual vocabulary, mature accessibility primitives, robust theming, and good React/Vite compatibility. It can provide dialogs, navigation, tables, and status components quickly.

**Costs:** introduces a substantial design system and migration surface for a small existing UI, adds bundle/dependency weight, and requires deliberate styling to avoid a Microsoft-product look that may not match the desired restrained custom shell. Existing plain semantic markup would still need migration and behavior verification.

### Material UI

**Strengths:** mature React ecosystem, strong documentation, broad component coverage, theming, accessibility support, and straightforward Vite integration.

**Costs:** larger dependency/runtime footprint than a small local layer, a more recognizable Material visual language that must be heavily themed, and additional learning/migration effort for styling, slots, and component APIs. Table/dialog/form replacements would touch many existing tests and selectors.

### Project-owned tokens and CSS Modules

**Strengths:** lowest bundle impact, no new runtime dependency, exact control over the restrained enterprise direction, incremental adoption around current semantic HTML, and simple compatibility with React 18 and Vite. CSS Modules isolate feature styling while global tokens keep the visual language coherent.

**Costs:** the team owns accessibility discipline, component conventions, browser testing, and long-term maintenance. Complex widgets should remain native or be added only when a repeated need is proven; the system should not grow into an undocumented replacement library.

### Recommendation

Use a **lightweight project-owned component system based on global design tokens and CSS Modules**, with native semantic HTML for tables, disclosure cards, forms, and dialogs wherever practical. Add a small set of shared primitives only for repeated behavior: page header, alert, status badge, loading skeleton, empty state, and modal dialog. This best fits the small existing surface, avoids unnecessary migration, keeps bundle impact low, and preserves API/component behavior while allowing a coherent enterprise UI. Re-evaluate Fluent UI or Material UI if the product expands into many complex settings, data grids, or standardized workflows that justify the dependency and migration cost.

## 6. Visual Acceptance Criteria

The remediation is visually acceptable when:

- Both functional areas share the same shell, navigation, typography, spacing, controls, status colors, alerts, and focus treatment.
- Chat has an immediately findable composer, visually distinct user/support messages, readable procedural answers, stable loading/error/empty states, and expandable source cards separated from answer text.
- Documents are scannable in a semantic table at laptop widths, with clear upload, status, detail, re-index, delete, warning, failure, and confirmation treatments.
- `/config/ai` can host grouped future settings without displaying credentials or implying an API contract change.
- Layout remains usable at the four target viewport sizes, at 200% zoom where applicable, and with long content.
- Keyboard-only users can navigate the shell, submit a question, expand sources, open/cancel/confirm the delete dialog, and recover from service/session errors.
- Existing behavior tests remain green; new component, responsive, accessibility, and screenshot checkpoints pass.
- No backend files, API contracts, RAG behavior, specifications, existing task IDs, or completed task statuses are changed as part of the UI remediation.
