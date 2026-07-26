# Follow-on: CLI resume, download, polish

**Prerequisite**: [`specs/001-network-file-upload-client/`](../001-network-file-upload-client/) — Phases **1–3** merged (browser upload MVP).

This milestone carries **deferred tasks `T021`–`T035`** from the original breakdown: resumable CLI upload (**US2**), list/download (**US3**), OAuth MAY docs (**US4**), integration tests and OpenAPI parity (**Phase 7**).

Feature `003-cli-auth-upload-sessions` accepted server upload-session primitives plus CLI login/config storage for `T021`-`T025`. Remaining follow-on work starts with the CLI resumable upload command (`T026`) in feature `004`.

Functional requirements remain defined in [`spec.md`](../001-network-file-upload-client/spec.md); [`tasks.md`](./tasks.md) is the execution checklist for this follow-on branch.
