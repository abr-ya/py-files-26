# Data Model: Network File Upload Client

Derived from `spec.md` Key Entities and functional requirements.

## User

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID PK | Internal identifier |
| `login` | str, unique | Case normalization rules enforced at API layer |
| `password_hash` | str | bcrypt |
| `created_at` | datetime | |
| `external_google_sub` | str, nullable | Reserved for OAuth Phase 2 |

**Rules**: Registration creates rows only when deployment policy allows (FR-010).

## StoredUploadObject

Represents an accepted file owned by a user (download target).

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID PK | Stable download identifier |
| `owner_user_id` | FK → User | |
| `original_filename` | str | User-visible name |
| `byte_size` | int | Must be ≤ 1 GB (spec FR-009) |
| `storage_path` | str | Relative path under `STORAGE_ROOT` |
| `sha256` | str, optional | Computed at finalize |
| `created_at` | datetime | Acceptance timestamp—TTL baseline |
| `expires_at` | datetime | `created_at + retention_days` |

**Rules**:

- Ownership enforced on every download (FR-008).
- Listing scoped to `owner_user_id` (minimal listing UX FR-002).

## UploadSession (resumable path — CLI / optional advanced browser)

Tracks partial uploads until promotion to `StoredUploadObject`.

| Field | Type | Notes |
|-------|------|------|
| `id` | UUID PK | Session token |
| `owner_user_id` | FK → User | Authenticated creator |
| `original_filename` | str | User-visible name propagated to finalized object |
| `expected_size` | int | Declared total bytes ≤ 1 GB |
| `received_bytes` | int | Must advance contiguously |
| `partial_storage_path` | str | Temp file |
| `state` | enum(`active`,`completed`,`failed`) | |
| `created_at` | datetime | GC stale sessions |

**Transitions**:

`active` → `completed` after finalize validates size/hash → creates `StoredUploadObject`, deletes partial temp.

`active` → `failed` on integrity/config errors.

## AuthSession / Token payload (JWT claims)

Not necessarily stored server-side beyond optional revocation table later MVP—minimal JWT contains:

- `sub`: user id  
- `exp`: expiry  
- `iat`: issued at  

## Relationships

```
User 1 ── * StoredUploadObject
User 1 ── * UploadSession
```

## Validation highlights

- Reject `expected_size` > **1 GB** (`1000000000` bytes SI cap aligned with OpenAPI `maximum`). Policy configurable downward via deployment env.
- TTL deletion removes filesystem blob then DB row—ordering avoids orphaned files.
