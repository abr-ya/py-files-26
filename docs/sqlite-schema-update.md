# SQLite Schema Update After Deploy

Use this guide when a remote py-files server has already been running with an existing SQLite database and a newer release adds additive schema fields.

The current bootstrap can backfill these legacy `upload_sessions` columns on SQLite:

- `original_filename`
- `sha256`

## Update Steps

1. Stop or drain the running backend.
2. Back up the SQLite database.
3. Deploy the new code.
4. Run the schema bootstrap explicitly, or start the backend once.
5. Verify the columns exist.
6. Restart the backend normally.

Example from the `server/` directory:

```bash
cp var/py_files.db var/py_files.db.backup-$(date +%Y%m%d-%H%M%S)

git pull
.venv/bin/pip install -e ".[dev]"

.venv/bin/python -c "from py_files_server.db import init_db; init_db()"
```

Verify the SQLite schema without requiring the `sqlite3` shell:

```bash
.venv/bin/python -c "import sqlite3; con=sqlite3.connect('var/py_files.db'); print([r[1] for r in con.execute('pragma table_info(upload_sessions)')])"
```

The output should include `original_filename` and `sha256`.

## Absolute Database Paths

If production uses an absolute `DATABASE_URL`, run the command from the same working directory and environment used by the backend, or export the same variable first:

```bash
export DATABASE_URL=sqlite:////opt/py-files/var/py_files.db
.venv/bin/python -c "from py_files_server.db import init_db; init_db()"
```

## Non-SQLite Databases

The automatic backfill is SQLite-only. If `DATABASE_URL` points to PostgreSQL, MySQL, or another database, add the equivalent migration manually before restarting the app.
