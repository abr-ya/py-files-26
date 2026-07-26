## 1. Source Inventory

- [x] 1.1 Inventory legacy source files under `specs/001-network-file-upload-client/` and `specs/002-network-file-upload-follow-on/`, classifying each as product requirement, implementation note, API contract, quickstart, checklist, or historical context.
- [x] 1.2 Compare the inventory against existing `openspec/specs/cli-resumable-upload/spec.md` to avoid duplicating Feature 003 accepted behavior.
- [x] 1.3 Record the final source mapping in this feature's closeout notes or updated backlog so future agents can see where each legacy area moved.

## 2. OpenSpec Accepted Specs

- [ ] 2.1 Add accepted `openspec/specs/browser-upload/spec.md` content for browser login/upload behavior, upload outcomes, retry guidance, and size-limit handling.
- [ ] 2.2 Add accepted `openspec/specs/auth-and-accounts/spec.md` content for login/password auth, registration policy, token/session expectations, and OAuth deferred status.
- [ ] 2.3 Add accepted `openspec/specs/stored-objects/spec.md` content for stored object metadata, ownership, retention/expiry, and deferred list/download routing.
- [ ] 2.4 Add accepted `openspec/specs/api-contract/spec.md` content for `/api/v1`, JSON metadata, binary content transfer, and OpenAPI contract authority.
- [ ] 2.5 Add accepted `openspec/specs/spec-governance/spec.md` content making `openspec/` the single current source of truth and requiring a legacy marker for `specs/`.

## 3. Legacy Marker And Routing

- [ ] 3.1 Add a root legacy notice in `specs/` that states the directory is historical/reference-only after this migration and points to `openspec/` for current requirements, backlog, active changes, and archives.
- [ ] 3.2 Update `openspec/backlog.md` so Sources Of Truth points to `openspec/specs/`, active/archived changes, and repo-local workflow docs instead of legacy `specs/`.
- [ ] 3.3 Renumber pending roadmap entries so feature `005` is this migration, List/Download moves to the next available feature number, and Docs/Verification Polish moves after it.
- [ ] 3.4 Preserve traceability from original task IDs `T021`-`T035` to the current OpenSpec backlog and future feature numbers.
- [ ] 3.5 Update `docs/agent-openspec-token-guide.md` if needed so future agents start from OpenSpec and treat `specs/` as legacy.

## 4. Cleanup And Validation

- [ ] 4.1 Search for wording that still presents `specs/` as current authority and update it to OpenSpec-first wording where appropriate.
- [ ] 4.2 Run `openspec validate feature-005-migrate-legacy-specs-to-openspec --strict`.
- [ ] 4.3 Run `openspec validate --changes --strict`.
- [ ] 4.4 Run `openspec validate --specs --strict` after accepted specs are synced or after archive.
- [ ] 4.5 Run `git diff --check`.
- [ ] 4.6 Archive the completed change only after validation is green and confirm that `openspec list` no longer shows feature `005` as active.
