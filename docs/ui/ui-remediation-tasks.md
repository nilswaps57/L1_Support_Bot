# UI Remediation Tasks

This is a frontend-only incremental task list. Execute in order. Each task preserves existing component behavior, routes, API contracts, response/session/document lifecycle rules, and existing tests unless a task explicitly adds coverage. Do not modify backend code, RAG behavior, `specs/`, existing task IDs, completed task status, or regenerate `specs/002-flexcube-support-chatbot/tasks.md`.

## Working Rules

- Use the existing React 18, TypeScript, Vite, React Router, React Query, and Testing Library stack.
- Do not install Fluent UI, Material UI, Redux, Zustand, or another global state store during this remediation.
- Prefer styling and small composition changes to replacing working components. Keep existing API modules and hooks intact unless a presentation-only state signal is needed.
- Keep user-safe error text. Do not render credentials, secrets, request IDs, checksums, chunk IDs, tracebacks, or filesystem paths as ordinary UI content.
- After each increment, run the narrowest relevant Vitest test, then the frontend build before moving to a wider visual checkpoint.

## Increment 1: Establish Tokens and Baseline Styles

- [ ] Add global design tokens for canvas/surface/ink/border/accent/semantic states, typography roles, the 4px spacing scale, radii, elevation, focus ring, and reduced-motion behavior in `frontend/src/styles/tokens.css`.
- [ ] Add the global reset, font stack, body sizing, button/input defaults, focus-visible treatment, responsive container utilities, and landmark defaults in `frontend/src/styles/global.css`.
- [ ] Import the global styles from `frontend/src/main.tsx` without changing application startup behavior.
- [ ] Add a small visual baseline note or screenshot fixture for the four target viewports in the frontend test/review process; do not change runtime behavior.
- [ ] Validate with `npm run test:run` and `npm run build` from `frontend/`.

## Increment 2: Build the Shared Shell

- [ ] Update `frontend/src/app/router.tsx` to apply the shell layout, persistent desktop left navigation, compact mobile navigation trigger, active link state, `aria-current`, and shell landmarks while retaining all existing route paths and redirects.
- [ ] Add `frontend/src/shared/components/PageHeader.tsx` and its style module only if the repeated title/description/action pattern cannot remain local to the pages; keep the component intentionally small.
- [ ] Add breadcrumbs for nested configuration pages in the existing page-header composition without adding routes or API calls.
- [ ] Use the existing `Chat`, `Configuration`, `Documents`, and `AI configuration` route labels; do not expose implementation identifiers.
- [ ] Extend `frontend/tests/components/app-routing.test.tsx` to assert active navigation, page landmarks, `aria-current`, heading hierarchy, and mobile-nav keyboard behavior.
- [ ] Add `frontend/tests/components/app-shell.test.tsx` only if shell behavior is separated enough to warrant a focused test; otherwise keep assertions in the routing test.

## Increment 3: Add Shared State Primitives

- [ ] Add `frontend/src/shared/components/Alert.tsx` and `frontend/src/shared/components/Alert.module.css` for info/success/warning/error presentation with consistent roles, labels, spacing, and live-region behavior.
- [ ] Add `frontend/src/shared/components/StatusBadge.tsx` and `frontend/src/shared/components/StatusBadge.module.css` for text-plus-indicator status treatment.
- [ ] Add `frontend/src/shared/components/LoadingSkeleton.tsx` and `frontend/src/shared/components/LoadingSkeleton.module.css` for stable page, conversation, detail, and table placeholders.
- [ ] Add `frontend/src/shared/components/EmptyState.tsx` and `frontend/src/shared/components/EmptyState.module.css` for concise task-oriented empty states with an optional action.
- [ ] Add focused assertions for roles, accessible names, contrast-oriented class/state contracts, and reduced-motion-safe markup in `frontend/tests/components/shared/state-primitives.test.tsx`.
- [ ] Keep existing direct messages and API error behavior intact while migrating one consumer at a time.

## Increment 4: Shape the Chat Page

- [ ] Update `frontend/src/features/chatbot/pages/ChatPage.tsx` to use the shared page header, conversation work area, compact session toolbar, stable composer region, and initial/session-unavailable states.
- [ ] Add a page-local stylesheet at `frontend/src/features/chatbot/pages/ChatPage.module.css` for desktop reading width, vertical rhythm, and responsive stacking; do not change the hook’s session or API behavior.
- [ ] Keep the composer available only when the existing session condition allows it, and make session creation/loading visible without moving the composer unpredictably.
- [ ] Update `frontend/src/features/chatbot/components/ChatSessionControls.tsx` to use the shared toolbar treatment, human-readable expiry label, stable pending/disabled state, and polite clear-session feedback.
- [ ] Update `frontend/tests/components/chatbot/chat-page.test.tsx` and `frontend/tests/components/chatbot/session.test.tsx` for empty, session-loading, expired-session, clear-session, and service-unavailable presentation while preserving current action assertions.

## Increment 5: Improve Composer and Message Reading

- [ ] Update `frontend/src/features/chatbot/components/ChatInput.tsx` and add `frontend/src/features/chatbot/components/ChatInput.module.css` for a prominent but balanced labelled composer, visible focus, stable submit button dimensions, disabled/pending treatment, and mobile layout.
- [ ] Update `frontend/src/features/chatbot/components/MessageList.tsx` and add `frontend/src/features/chatbot/components/MessageList.module.css` for a readable conversation stream, empty state, stable list semantics, and preserved submitted questions.
- [ ] Update `frontend/src/features/chatbot/components/MessageBubble.tsx` and add `frontend/src/features/chatbot/components/MessageBubble.module.css` for distinct `You` and `Support` roles, answer reading width, paragraphs/lists/line breaks, and separation between answer and sources.
- [ ] Keep answer text and citation data unchanged; do not add client-side interpretation of API answer semantics.
- [ ] Expand `frontend/tests/components/chatbot/chat-page.test.tsx` or add `frontend/tests/components/chatbot/message-presentation.test.tsx` to cover role labels, long-answer wrapping, empty state, and keyboard focus order.

## Increment 6: Normalize Chat Response States

- [ ] Update `frontend/src/features/chatbot/components/ResponseState.tsx` and add `frontend/src/features/chatbot/components/ResponseState.module.css` to use shared alert/state treatments for grounded, partial, ambiguous, incorrect-premise, insufficient, expired-session, and service-error outcomes.
- [ ] Update `frontend/src/features/chatbot/components/ClarificationPrompt.tsx` and its local styles so clarification is visually actionable and remains separate from a normal grounded answer.
- [ ] Ensure live-region roles are limited to meaningful state transitions and do not repeatedly announce static message history.
- [ ] Extend `frontend/tests/components/chatbot/response-states.test.tsx` and `frontend/tests/components/chatbot/multi-source-and-ambiguity.test.tsx` for every response state, alert/status role, preserved answer, and no-source behavior.

## Increment 7: Convert Sources into Citation Cards

- [ ] Update `frontend/src/features/chatbot/components/CitationList.tsx` and add `frontend/src/features/chatbot/components/CitationList.module.css` for a labelled sources region, count/heading treatment, responsive spacing, and separation from answer content.
- [ ] Update `frontend/src/features/chatbot/components/CitationItem.tsx` and add `frontend/src/features/chatbot/components/CitationItem.module.css` to use native `details/summary` disclosure cards. Show document name and strongest locator in the summary; show available metadata as labelled fields only when expanded.
- [ ] Keep multi-source ordering and omission of unavailable fields. Hide raw chunk IDs and other internal metadata from the ordinary presentation without changing the citation API type.
- [ ] Extend `frontend/tests/components/chatbot/citation-list.test.tsx` for collapsed/expanded keyboard disclosure, accessible source names, multi-source preservation, omitted fields, and answer/source separation.

## Increment 8: Create the Configuration Page Hierarchy

- [ ] Update `frontend/src/features/configuration/pages/DocumentsPage.tsx` to use the shared page header, prominent upload action region, document-management content area, and responsive detail placement.
- [ ] Replace the current configuration route boundary in `frontend/src/app/router.tsx` only as needed to provide a future-compatible visual page shell for `/config/ai`; do not add functional AI settings or API calls.
- [ ] Add `frontend/src/features/configuration/pages/AIConfigurationPage.tsx` only if a dedicated future-compatible page component is needed. It should contain grouped, non-secret setting placeholders or empty state language, never credentials or secrets.
- [ ] Add page-local styles in `frontend/src/features/configuration/pages/DocumentsPage.module.css` and, if created, `frontend/src/features/configuration/pages/AIConfigurationPage.module.css`.
- [ ] Extend `frontend/tests/components/app-routing.test.tsx` for page title, breadcrumb, and future AI configuration shell expectations without asserting unimplemented behavior.

## Increment 9: Make Document Management Scannable

- [ ] Update `frontend/src/features/configuration/components/DocumentList.tsx` and add `frontend/src/features/configuration/components/DocumentList.module.css` to render a semantic table on laptop widths with name/type, source, status, indexed chunks, updated date, and a predictable detail/action affordance.
- [ ] Preserve the existing `listDocuments` and `getDocument` query keys, selection behavior, and detail fetch. Do not change pagination or API response handling.
- [ ] Use `LoadingSkeleton` for table-shaped loading, `EmptyState` for no documents, and `Alert` for load/detail failures while preserving current accessible status/error messages.
- [ ] Keep selected document details in a clearly bounded region or responsive side panel. Avoid nested cards and avoid hiding lifecycle actions on narrow screens.
- [ ] Extend `frontend/tests/components/configuration/document-lifecycle.test.tsx` and add `frontend/tests/components/configuration/document-list.test.tsx` for table headers, row selection, loading, empty, failure, long names, and responsive-safe action access.

## Increment 10: Refine Upload and Lifecycle Controls

- [ ] Update `frontend/src/features/configuration/components/DocumentUpload.tsx` and add `frontend/src/features/configuration/components/DocumentUpload.module.css` for a labelled upload surface, grouped fields, helper text, validation/error/success regions, stable pending button, and mobile stacking.
- [ ] Keep accepted extensions and upload-size validation aligned with the value supplied by
the existing application configuration or API contract. Do not hard-code a new UI-only limit.
- [ ] Update `frontend/src/features/configuration/components/DocumentStatus.tsx` and add `frontend/src/features/configuration/components/DocumentStatus.module.css` to consume `StatusBadge`, preserve all current human-readable labels, and distinguish active, ready, warning, failed, deleting, and deleted states with text and non-color indicators.
- [ ] Update `frontend/src/features/configuration/components/IngestionWarnings.tsx` and add `frontend/src/features/configuration/components/IngestionWarnings.module.css` for a concise warning summary with expandable details and readable page context. Keep warning content user-safe.
- [ ] Update `frontend/src/features/configuration/components/ReindexDocumentButton.tsx` and its styles for secondary-action hierarchy, stable pending state, and nearby success/error feedback without changing mutation behavior.
- [ ] Extend `frontend/tests/components/configuration/document-upload.test.tsx` and `frontend/tests/components/configuration/document-status.test.tsx` for keyboard labels, pending/disabled states, warning disclosure, and non-color status cues.

## Increment 11: Finish Destructive Dialog Accessibility

- [ ] Update `frontend/src/features/configuration/components/DeleteDocumentDialog.tsx` and add `frontend/src/features/configuration/components/DeleteDocumentDialog.module.css` for a real modal surface, backdrop, consequence text, secondary cancel action, and clearly destructive confirmation.
- [ ] Add focus placement, focus containment, Escape close, focus return, and pending-state behavior using a small local implementation or a focused shared modal primitive. Do not alter delete API behavior or mutation timing.
- [ ] Keep the current document name, confirmation wording intent, user-safe API error, and successful refresh behavior.
- [ ] Extend `frontend/tests/components/configuration/document-lifecycle.test.tsx` or add `frontend/tests/components/configuration/delete-document-dialog.test.tsx` for dialog labelling, keyboard-only cancel/confirm, Escape, focus return, pending controls, and conflict error presentation.

## Increment 12: Responsive Review Checkpoint

- [ ] Add executable Playwright coverage in `frontend/tests/e2e/setup.spec.ts` or a focused new spec under `frontend/tests/e2e/` for chat, documents, upload, citation disclosure, mobile navigation, and delete dialog at 1280x800, 1024x768, 768x1024, and 375x812.
- [ ] Use stable fixtures/mocks for frontend states so the checks do not change backend behavior or depend on RAG output.
- [ ] Capture screenshot checkpoints for the shell, empty chat, grounded/partial chat, citation-expanded answer, documents table, upload validation, document warning, and delete dialog. Review for clipping, overlap, unexpected scroll, layout shift, and readable long content.
- [ ] Add a 200% zoom/reflow pass where supported and verify long document names, status labels, buttons, alerts, and assistant answers remain usable.

## Increment 13: Accessibility Review Checkpoint

- [ ] Run keyboard-only checks through the shell, navigation, composer, citation disclosures, document selection, upload controls, re-index action, and delete dialog.
- [ ] Add focused Testing Library assertions for landmark/heading order, accessible names, `aria-current`, alert/status semantics, dialog focus, and source disclosure. Use an automated axe-style scan only if it can be added without introducing a UI component dependency.
- [ ] Verify color contrast for normal text, selected navigation, controls, status badges, warning/error surfaces, borders, and focus indicators; verify `prefers-reduced-motion` behavior.
- [ ] Record visual and accessibility findings beside the relevant screenshot checkpoint, then fix only frontend presentation defects discovered in this scope.

## Increment 14: Final Regression and Handoff

- [ ] Run `npm run test:run` from `frontend/` and confirm all existing behavior tests plus new UI tests pass.
- [ ] Run `npm run build` from `frontend/` and confirm TypeScript/Vite output is clean.
- [ ] Run the focused Playwright responsive/screenshot suite and review the generated artifacts.
- [ ] Confirm `git diff --name-only` shows only the intended frontend UI files and the two planning documents for this work; do not revert unrelated pre-existing worktree changes.
- [ ] Confirm no backend files, API contracts, RAG logic, `specs/`, existing task IDs, or completed task status were changed.
- [ ] Update the UI documentation only if the implemented visual behavior materially differs from `docs/ui/ui-specification.md`; do not regenerate or modify the existing feature task list.

## Definition of Done

- The shell, chatbot, and configuration surfaces use one coherent tokenized visual system.
- Existing chat/session/document/upload/re-index/delete behavior remains intact.
- Chat states and sources are readable, explicit, and visually separated.
- Documents are scannable as a responsive management table with clear lifecycle actions and warnings.
- Destructive actions are confirmed through an accessible modal.
- Component tests, responsive checks, accessibility checks, and screenshot review checkpoints are present and passing.
- No UI library, Redux, Zustand, backend behavior, API contract, RAG logic, specification, existing task ID, or completed task status was changed as part of the remediation plan.
