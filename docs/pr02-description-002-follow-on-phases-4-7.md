# Pull request description — Follow-on feature `002` (Phases 4–7)

**Branch**: `002-network-file-upload-follow-on` · **Spec / tasks**: [`specs/002-network-file-upload-follow-on/`](../specs/002-network-file-upload-follow-on/)

Suggested PR title:

**feat: follow-on `002` — CLI resumable upload, list/download, Phase 6–7 polish**

---

## Summary

Completes the deferred work from the browser MVP (`001`) through **Phase 4–7** (**`T021`–`T035`**): resumable **`/api/v1/upload-sessions`** plus Python CLI **`pyfiles login` / `pyfiles upload`** (with resume sidecar); object **listing**, **metadata**, and **octet-stream download** for the owner in API, browser UI, and **`pyfiles download`**; explicit **OAuth MAY** documentation in the plan; **OpenAPI** alignment with runtime behavior; **integration** tests (round-trip and TTL denial); and an updated **quickstart**.

The follow-on **`spec.md`** was expanded from a stub into a full stakeholder-facing specification; **`tasks.md`** marks **`T021`–`T035`** complete.

---

## What’s included

### Phase 4 — CLI resumable upload (US2)

- **API**: **`POST /api/v1/upload-sessions`**, **`GET /api/v1/upload-sessions/{session_id}`** (progress for resume), **`PATCH ...`** with header **`Upload-Offset`**, **`POST .../complete`** → **`StoredObjectMeta`** (201).
- **Server**: **`original_filename`** on **`UploadSession`**; services **`upload_session_service`**, **`upload_finalize`** (contiguous chunks, promote partial → blob, SHA-256 at finalize).
- **CLI**: **`~/.config/py-files/config.json`** (and Windows **`%APPDATA%\py-files\`**) for **`base_url`** + JWT; **`pyfiles upload`** with optional **`tqdm`**, **`--resume`**, sidecar **`{file}.pyfiles-session`**.
- **Tests**: [`server/tests/test_upload_sessions.py`](../server/tests/test_upload_sessions.py).

### Phase 5 — List & download (US3)

- **API**: **`GET /api/v1/objects`**, **`GET /api/v1/objects/{id}`**, **`GET /api/v1/objects/{id}/content`** (**`FileResponse`**, generic **404** for wrong owner / missing blob / TTL).
- **Server**: **`object_lookup`** helpers; SQLite naive **`expires_at`** normalized for comparisons (**`_as_utc`**).
- **Frontend**: **“Your files”** table, **Refresh**, blob download via authenticated **`fetch`**.
- **CLI**: **`pyfiles download <object_uuid>`** with streaming write and **`Content-Disposition`** filename parsing.
- **Tests**: [`server/tests/test_objects_list_download.py`](../server/tests/test_objects_list_download.py).

### Phase 6 — OAuth / Google (**FR-006 MAY**, docs only)

- **Plan**: new **“Deferred / optional scope”** section in [`plan.md`](../specs/001-network-file-upload-client/plan.md); **Frontend** diagram filename corrected to **`style.css`**.

### Phase 7 — Polish

- **OpenAPI**: Extra documented status codes (**401**, **404**, **409**, **413** where applicable); multipart **`file`** **`required`**; clarifying descriptions (**[`contracts/openapi.yaml`](../specs/001-network-file-upload-client/contracts/openapi.yaml)**).
- **Integration**: [`server/tests/integration/test_roundtrip.py`](../server/tests/integration/test_roundtrip.py), [`server/tests/integration/test_ttl_denial.py`](../server/tests/integration/test_ttl_denial.py) (fixture resets DB + storage per test).
- **Docs**: Revised [`quickstart.md`](../specs/001-network-file-upload-client/quickstart.md) (uvicorn app path, `/health` vs **`/api/v1`**, CLI examples).
- **Lockfile**: [`server/uv.lock`](../server/uv.lock) for reproducible dev installs via **uv**.

### Spec kit artifacts (`002`)

- [`spec.md`](../specs/002-network-file-upload-follow-on/spec.md): full specification for the follow-on milestone.
- [`checklists/requirements.md`](../specs/002-network-file-upload-follow-on/checklists/requirements.md).
- [`.specify/feature.json`](../.specify/feature.json) → **`specs/002-network-file-upload-follow-on`** (when committing this branch tip).

---

## How to verify

```bash
cd server && uv run pytest -q
uv run uvicorn py_files_server.main:app --reload --host 127.0.0.1 --port 8000
```

Open **`http://127.0.0.1:8000/`** — register (if allowed), sign in, upload via browser; use **Refresh** and **Download** on **Your files**.

**CLI smoke** (from repo root):

```bash
cd clients/python && uv pip install -e .
pyfiles login --base-url http://127.0.0.1:8000 --login USER --password PASS
pyfiles upload ./some-file.bin
pyfiles download <object-uuid-from-json-output> -o ./out.bin
```

---

## Out of scope

- **Google OAuth**: documented as deferred (**FR-006 MAY**); no provider routes or UI affordances shipped.
- **Production hardening**: e.g. Schemathesis / extended contract CI (mentioned as optional in **quickstart**).

---

## Notes for reviewers

- **Variant C** from **`001`** (upload → download round-trip **and** CLI resumable path) is **in scope for this branch** relative to **`001`**’s Phase 3–only cutoff.
- **Existing SQLite DBs** created before **`UploadSession.original_filename`** may need recreation or migration if schemas drift in long-lived dev databases.
- **PR title / commit conventions**: this branch mixes **`feat`** (API/UI/CLI), **`docs`** (plan, quickstart, OpenAPI wording), **`test`** (integration); adjust squash message if your team prefers a single conventional type.
