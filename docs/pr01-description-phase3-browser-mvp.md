# Pull request description — Phase 3 browser MVP (`001`)

Suggested title:

**feat: browser MVP — auth, multipart upload, deferred follow-on (`002`)**

---

## Summary

Delivers **Phase 1–3** of the network file upload client (`T001`–`T020`): FastAPI backend with JWT auth, SQLite metadata, filesystem blob storage with TTL purge hook, **`POST /api/v1/objects`** multipart upload with **`MAX_UPLOAD_BYTES`** enforcement (**413** when exceeded), and a vanilla JS browser UI with upload progress.

Deferred work (**`T021`–`T035`**: CLI resumable upload, list/download, OAuth MAY docs, polish) is tracked under **`specs/002-network-file-upload-follow-on/`**. **`spec.md`** / **`tasks.md`** document this incremental boundary.

---

## What’s included

- **API**: `/health`, `/api/v1/auth/register`, `/api/v1/auth/login`, **`POST /api/v1/objects`** (multipart field `file`).
- **Frontend**: `GET /` serves **`index.html`**; static **`/static`** (`app.js`, styles).
- **Storage**: SQLite + blobs under configurable **`DATABASE_URL`** / **`STORAGE_ROOT`** (defaults documented); **`.gitignore`** excludes runtime **`server/var/`** and repo **`/var/`**.
- **Tests**: pytest (`upload`, **`413`** override, index HTML); **`bcrypt`** pinned **`<5`** for passlib compatibility.

---

## How to verify

```bash
cd server && pip install -e ".[dev]" && pytest
uvicorn py_files_server.main:app --reload
```

Open **`http://127.0.0.1:8000/`** — register (if enabled), sign in, upload a file; confirm success/error in the UI.

---

## Out of scope (follow-on)

See **`specs/002-network-file-upload-follow-on/tasks.md`** — CLI resume (`upload-sessions`), **`GET`** objects listing/content download, extended polish/OpenAPI parity/integration tests (**`T021`–`T035`**).

---

## Notes for reviewers

- **Variant C** (download round-trip + CLI resume per original clarifications) is **not** claimed by this PR; **`spec.md`** states that explicitly until **`002`** lands.
