# Frontend and product-site task plan (F01–F12)

This extends, rather than replaces, T04/T17/T18 and later backend gates. The current `apps/web/src/App.tsx` is a stub. The Lovable design prototype is not the Git-synced source of truth until a specific revision is imported and reviewed. Build a usable console first. A product marketing site can grow alongside it, but its claims must reflect shipped capabilities.

## Design and runtime contract

- Visual direction: clean typography, restrained color and motion, clear product vocabulary, high information density only where an operator needs it. Use Veza and TrueFoundry as interaction references, not copied assets or markup.
- Use existing React + TypeScript + Vite + Tailwind primitives; keep design tokens in CSS and accessible reusable components. Use actual licensed service marks only where an integration exists, and label `planned` or `unsupported` when it does not.
- Never invent a customer logo, testimonial, certification, detection count, compliance status or recorded walkthrough. A real video follows a working product gate; before then use a clearly labeled prototype tour.
- Every screen distinguishes loading, empty, error, denied, stale and partial states. Never display a synthetic green badge as a live result.
- All sensitive previews are masked by the API; client-side CSS masking is not a security boundary. Avoid raw source text in URL, browser storage, analytics or error telemetry.
- Breakpoint acceptance: 320/360/390 px phones, 768 px tablet, 1024 px laptop, 1440/1920 px desktop, 2560/3840 px high-resolution display. Test at 200% zoom and long labels. Wide views use bounded content widths; mobile navigation remains usable with touch and keyboard.
- Respect `prefers-reduced-motion`; provide pause/control for auto-playing media; keep focus visible. Content and forms must function without animation.

## F01 — Design foundation

**Start:** `apps/web/src/index.css`, reusable UI components and route shell. Document color, type, spacing, focus, elevation, density, icon use and chart semantics. Create component states for loading, stale, partial and error. Keep brand/system colors from communicating severity alone.

**Verify:** Storybook or equivalent isolated component states, automated contrast checks plus keyboard/manual screen-reader pass. Check dark/light if both offered. **Pass:** components adapt from 320 px to 3840 px without horizontal clipping or unreadable body text. **Fail:** color-only status, focus loss, text truncation hiding a security decision. **Depends on:** T02 web build.

## F02 — Live System view

**Start:** T04's `/api/v1/system`, `/livez`, `/readyz`. Add a typed API client generated from the same reviewed OpenAPI revision. Fetch real install ID/build revision; show loading, unavailable and recovered states. Do not store a dev token in shipped JavaScript.

**Verify:** Playwright against live Compose; compare DB row, API response and rendered ID; API/DB restart and network timeout. **Pass:** browser state tracks live service state across refresh and failure. **Fail:** hardcoded status or a success badge after outage. **Depends on:** T04.

## F03 — Authentication and tenant context

**Start:** T06 session endpoint and OIDC browser redirect. Build sign-in/out, expired-session, forbidden and tenant selection flows. Display tenant from server-derived membership. Restore only safe navigation state after redirect.

**Verify:** Admin, analyst and viewer browser sessions, direct URL, refresh, logout, expired cookie, role change and two tabs. Cross-check backend denial. **Pass:** UI permission affordances and API permissions agree; stale sessions do not show protected data. **Fail:** browser local storage or a URL parameter becomes identity/tenant authority. **Depends on:** T05/T06.

## F04 — Sources and connector coverage

**Start:** T09/T10 source endpoints and capability metadata. Present source type, read-only scope, last successful/attempted scan, permission/format limitations and onboarding steps. For the fixture, accept an approved server-side root reference rather than a browser-supplied arbitrary path.

**Verify:** Operator creates source; viewer is denied by API; invalid/duplicate/unavailable source shows actionable error. Confirm requested source cannot write to fixture. **Pass:** operator can identify exactly what was and was not enumerated. **Fail:** source tile says `connected` on incomplete access. **Depends on:** T09/T10.

## F05 — Scans, inventory and data classification

**Start:** T11–T15 scans, assets, outcomes and masked classification APIs. Show a scan state machine, progress based on persisted counts, retry/cancel status, denominator, unsupported reason and last-observed time. An inventory row links to provenance without exposing raw sensitive values.

**Verify:** Live scan, encrypted/image-only PDF, oversized file, malformed file, partial enumeration, cancellation and API restart. Refresh during a scan. **Pass:** counts remain consistent, unsupported never means clean, and a partial run never tombstones unseen assets. **Fail:** fake spinner, silent skip or stale success. **Depends on:** T11–T15.

## F06 — Findings and AI access paths

**Start:** T16/T17 findings, risk explanation, evidence confidence and declared AI-resource bindings. Display source → asset → AI application as evidence-backed graph paths. Distinguish declared, observed and verified edges; show source version and timestamp. Provide finding workflow actions only to authorized roles.

**Verify:** Payroll finding linked to HR Bot; rescan without duplicate finding; tenant collision, missing edge, masked canary, revoked role and mobile graph fallback to an accessible ordered list. **Pass:** an operator can explain why a finding exists and what evidence is absent. **Fail:** inferred access appears as verified permission. **Depends on:** T16–T18.

## F07 — Protected RAG explanation

**Start:** T19–T26 decision trace API. Show source/version/ACL/policy revisions, whether content was retrieved, decision reason, principal and freshness. Do not show Bob's forbidden chunk in DOM, network response, source map or analytics.

**Verify:** Alice allow, Bob deny, unknown ACL, revocation, source outage, cache invalidation and direct URL attempts in live browser. Inspect the model fixture input, not only UI text. **Pass:** UI explanation matches actual pre-model authorization. **Fail:** denied content reached any model-facing path. **Depends on:** T26.

## F08 — Runtime policies and event exploration

**Start:** T27–T34 policy versions, simulation, managed route status and redacted events. Show monitor/block/mask behavior, policy revision, enforcement point and blind spots. Streaming states expose what is held and when content can leave.

**Verify:** Live blocked/masked synthetic prompts and outputs, malformed payload, provider outage, retry, streaming interruption and bypass attempt. **Pass:** browser policy state equals backend decisions; no unobserved managed path is called protected. **Fail:** a copy change suggests universal leak prevention. **Depends on:** T34.

## F09 — Agent and MCP workspace

**Start:** T35–T42 and D13/D14. Inventory agents, identities, tools, MCP servers, approved scopes, observed use and permission changes. Tool approval shows exactly the arguments/resource/action and expires within a bounded scope.

**Verify:** wrong user, wrong tool, expanded arguments, changed server metadata, reused approval and denied side effect. **Pass:** every tool decision has a named trusted principal and evidence. **Fail:** server-supplied description is treated as authorization. **Depends on:** T42.

## F10 — Code-to-cloud graph and connectors

**Start:** D01–D19 and T43–T50. Render repository/commit → build/artifact → deployment → workload identity → model/tool → source data, with provenance, collection timestamps and confidence. Provide filters by tenant, service, environment, code owner and unsupported signal.

**Verify:** one real fixture path with independently known IDs, then connector-specific live tests; conflicting and absent signals; node duplicates; tenant switch; large graph accessibility. **Pass:** incorrect correlation can be inspected and corrected without rewriting history. **Fail:** code import is labeled a running AI call or unknown SaaS internals are shown as mapped. **Depends on:** selected connectors.

## F11 — Lifecycle, DSPM and remediation workflows

**Start:** L01–L31 and T51–T56. Offer purpose, dataset lineage, training/evaluation/release, drift, exception, retirement and retention views. Remediation is a separate preview → scoped approval → execute → readback → path retest → audit workflow. Show unresolved copies and blocked writes.

**Verify:** dry run, missing approval, source write denial, partial failure, retry, stale source revision, rollback, retained backup and disconnected execution. **Pass:** closure is based on verified source/path state. **Fail:** request accepted or UI removed is treated as remediation success. **Depends on:** policy and scoped writer integration.

## F12 — Product landing pages and walkthrough

**Start:** after a stable P1 walkthrough; adapt the existing frontend design without mixing demo telemetry into operator data. Provide concise hero, exact capability map, visible deployment boundary, supported connectors and learn-more pages. Add a real captured P1 walkthrough at T18; replace it with richer footage only as those flows ship. A centered floating navbar may compact on scroll, but it must preserve keyboard order, focus and mobile menu behavior. Scroll transitions must respect reduced motion.

**Verify:** real video captions/transcript/poster; play/pause, focus and reduced-motion settings; route and hash navigation; viewport matrix; Lighthouse or equivalent performance/accessibility checks; no layout shift from media. Review every capability statement against `docs/scope.json` and the latest release evidence. **Pass:** product claims and visible demo match a verified release. **Fail:** unverified SOC 2/HIPAA/GDPR claim, fake customer/service logo, or prototype shown as production footage.

## Shared browser acceptance script

At T18, run: login → source registration → scan → inventory/coverage → masked finding → declared HR Bot path → rescan. At T26, add Alice/Bob retrieval and revocation. Record browser build revision, API commit, test fixture seed, screen sizes, console errors and sanitized screenshots. Run the flow with live Compose services, including one API restart and one failed dependency. Test keyboard-only navigation and reduced motion separately. The browser run is a release check, not a substitute for backend authorization or database assertions.

## F13–F17 — Non-human identity and SPIFFE extension

Extend the inventory and add workload detail, trust-domain/federation and identity-to-policy decision screens. Cross-link agent, MCP, graph and data views. The detailed route, state, data and negative-test contract is in `NHI_SPIFFE_FRONTEND_AND_BACKEND.md`. These screens may ship as **sample-only** before N01–N09 backend work, but the UI must never equate a verified SPIFFE identity with authorization or call a browser simulation runtime enforcement.
