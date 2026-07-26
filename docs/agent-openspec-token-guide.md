# Agent OpenSpec And Token Guide

This guide is the working rulebook for Codex agents in this repository. Follow it before changing OpenSpec artifacts or spending context on broad repo exploration.

## OpenSpec Workflow

1. Start from live repository state, not memory alone.
2. Read the smallest useful set first:
   - `openspec/config.yaml`
   - `openspec/backlog.md` when it exists
   - the active change under `openspec/changes/<change-id>/`
   - accepted specs under `openspec/specs/`
   - related source/spec files named by the task
3. For implementation work, run OpenSpec status/instructions before coding when available:
   - `openspec status --change <change-id> --json`
   - `openspec instructions apply --change <change-id> --json`
4. Preserve feature numbering and original task IDs from `openspec/backlog.md`; use `docs/legacy-specs/*` only for historical traceability when OpenSpec points there.
5. Keep completed and deferred work clearly separated:
   - completed phases stay marked as done
   - deferred phases remain unchecked and point to their source spec/task files
6. Update docs/specs in the same slice when behavior, API contracts, deployment steps, or user-facing workflows change.
7. Before archiving or calling a change complete, verify tests and OpenSpec validation, then record the exact commands.

## Token Budget Rules

1. Prefer targeted reads over broad scans.
2. Use `rg`/`find` for file discovery, then read only the relevant files.
3. Read file headers, task lists, and affected functions before opening entire large files.
4. Summarize findings briefly in chat; keep detailed state in repo markdown.
5. Avoid repeating full plans when a checklist already exists. Point to the checklist and name the next item.
6. Batch independent file reads in parallel.
7. Do not re-read unchanged files unless the answer depends on exact wording.
8. Keep user updates short: what was checked, what was learned, what is next.
9. Prefer small, bounded implementation slices with one verification pass per slice.
10. When blocked by environment/tooling, state the limit directly and stop digging sideways.

## Default Repo Loop

1. Reality check: `git status --short`, relevant docs/specs, current backlog.
2. Choose the smallest next task that preserves numbering and accepted scope.
3. Make focused edits near the affected surface.
4. Run the narrowest meaningful validation.
5. Report changed files, validation, and remaining next step.

## Legacy Specs

The legacy specs tree lives at `docs/legacy-specs/` and is reference-only after the OpenSpec migration. Current requirements, roadmap routing, active changes, and archive history should be read from `openspec/` first. Open `docs/legacy-specs/*` only when you need original task IDs, historical Spec Kit context, or a file explicitly referenced by an active OpenSpec task.
